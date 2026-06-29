use chrono::Utc;
use uuid::Uuid;

use crate::{
    app::app_error::{AppError, AppResult},
    domain::entities::{
        enums::BracketType,
        tournament::tournament::{
            BracketMatch, BracketMetadata, BracketParticipant, BracketStage, GeneratedBracket,
            MatchAdvance, MatchSlot, StageKind, TournamentTeam,
        },
    },
};

#[derive(Clone, Default)]
pub struct BracketService;

impl BracketService {
    pub fn generate(
        &self,
        tournament_id: Uuid,
        bracket_type: BracketType,
        teams: Vec<TournamentTeam>,
    ) -> AppResult<GeneratedBracket> {
        let participants = seeded_participants(teams);

        if participants.len() < 2 {
            return Err(AppError::Validation(
                "Bracket generation requires at least two teams".to_string(),
            ));
        }

        match bracket_type {
            BracketType::Se => Ok(generate_single_elimination(tournament_id, participants)),
            BracketType::De => generate_double_elimination(tournament_id, participants),
            BracketType::Rr => Ok(generate_round_robin(tournament_id, participants)),
            BracketType::Sw => generate_swiss(tournament_id, participants),
        }
    }
}

fn generate_single_elimination(
    tournament_id: Uuid,
    participants: Vec<BracketParticipant>,
) -> GeneratedBracket {
    let bracket_size = next_power_of_two(participants.len().max(2));
    let seeds = standard_seeding(bracket_size);
    let seeded_slots = first_round_slots(&participants, &seeds);
    let round_count = bracket_size.ilog2() as usize;
    let mut stages = Vec::with_capacity(round_count);

    for round in 1..=round_count {
        let matches_in_round = bracket_size >> round;
        let mut matches = Vec::with_capacity(matches_in_round);
        for match_index in 0..matches_in_round {
            let match_id = format!("WB-R{round}-M{}", match_index + 1);
            let slots = if round == 1 {
                let base_index = match_index * 2;
                vec![
                    seeded_slots[base_index].clone(),
                    seeded_slots[base_index + 1].clone(),
                ]
            } else {
                let prev_match_base = match_index * 2;
                vec![
                    source_slot(
                        1,
                        format!("WB-R{}-M{}", round - 1, prev_match_base + 1),
                        "winner",
                    ),
                    source_slot(
                        2,
                        format!("WB-R{}-M{}", round - 1, prev_match_base + 2),
                        "winner",
                    ),
                ]
            };

            let advances_to = if round < round_count {
                vec![MatchAdvance {
                    outcome: "winner".to_string(),
                    target_match_id: format!("WB-R{}-M{}", round + 1, (match_index / 2) + 1),
                    target_slot: if match_index % 2 == 0 { 1 } else { 2 },
                }]
            } else {
                Vec::new()
            };

            matches.push(BracketMatch {
                id: match_id,
                label: if round == round_count {
                    "Final".to_string()
                } else {
                    format!("Round {round} Match {}", match_index + 1)
                },
                round,
                best_of: 1,
                slots,
                advances_to,
            });
        }

        stages.push(BracketStage {
            id: format!("winners-round-{round}"),
            label: if round == round_count {
                "Final".to_string()
            } else {
                format!("Winners Round {round}")
            },
            round,
            kind: StageKind::Winners,
            matches,
        });
    }

    GeneratedBracket {
        tournament_id,
        bracket_type: BracketType::Se,
        generated_at: Utc::now(),
        participants,
        stages,
        metadata: BracketMetadata {
            rounds: round_count,
            bracket_size: Some(bracket_size),
            grand_final_reset: false,
            pairing_strategy: Some("standard_seeded_single_elimination".to_string()),
            notes: vec![
                "Bracket is seeded by team creation order, then name.".to_string(),
                "Byes are injected to the first round when participant count is not a power of two."
                    .to_string(),
            ],
        },
    }
}

fn generate_double_elimination(
    tournament_id: Uuid,
    participants: Vec<BracketParticipant>,
) -> AppResult<GeneratedBracket> {
    if participants.len() < 4 {
        return Err(AppError::Validation(
            "Double elimination requires at least four teams".to_string(),
        ));
    }

    let bracket_size = next_power_of_two(participants.len());
    let winners = generate_single_elimination(tournament_id, participants.clone());
    let winners_rounds = bracket_size.ilog2() as usize;
    let mut stages = winners.stages;

    for losers_round in 1..=(winners_rounds.saturating_sub(1) * 2) {
        let injection_round = losers_round % 2 == 0;
        let stage_index = if injection_round {
            losers_round / 2 + 1
        } else {
            losers_round.div_ceil(2)
        };
        let match_count = bracket_size >> (stage_index + 1);
        let mut matches = Vec::with_capacity(match_count.max(1));

        for match_index in 0..match_count.max(1) {
            let match_id = format!("LB-R{losers_round}-M{}", match_index + 1);
            let slots = if losers_round == 1 {
                vec![
                    source_slot(1, format!("WB-R1-M{}", match_index * 2 + 1), "loser"),
                    source_slot(2, format!("WB-R1-M{}", match_index * 2 + 2), "loser"),
                ]
            } else if injection_round {
                vec![
                    source_slot(
                        1,
                        format!("LB-R{}-M{}", losers_round - 1, match_index + 1),
                        "winner",
                    ),
                    source_slot(
                        2,
                        format!("WB-R{}-M{}", stage_index, match_index + 1),
                        "loser",
                    ),
                ]
            } else {
                vec![
                    source_slot(
                        1,
                        format!("LB-R{}-M{}", losers_round - 1, match_index * 2 + 1),
                        "winner",
                    ),
                    source_slot(
                        2,
                        format!("LB-R{}-M{}", losers_round - 1, match_index * 2 + 2),
                        "winner",
                    ),
                ]
            };

            let advances_to = if losers_round < (winners_rounds - 1) * 2 {
                let target_match = if injection_round {
                    format!("LB-R{}-M{}", losers_round + 1, (match_index / 2) + 1)
                } else {
                    format!("LB-R{}-M{}", losers_round + 1, match_index + 1)
                };
                vec![MatchAdvance {
                    outcome: "winner".to_string(),
                    target_match_id: target_match,
                    target_slot: if injection_round || match_index % 2 == 0 {
                        1
                    } else {
                        2
                    },
                }]
            } else {
                vec![MatchAdvance {
                    outcome: "winner".to_string(),
                    target_match_id: "GF-M1".to_string(),
                    target_slot: 2,
                }]
            };

            matches.push(BracketMatch {
                id: match_id,
                label: format!("Losers Round {losers_round} Match {}", match_index + 1),
                round: losers_round,
                best_of: 1,
                slots,
                advances_to,
            });
        }

        stages.push(BracketStage {
            id: format!("losers-round-{losers_round}"),
            label: format!("Losers Round {losers_round}"),
            round: losers_round,
            kind: StageKind::Losers,
            matches,
        });
    }

    stages.push(BracketStage {
        id: "grand-final".to_string(),
        label: "Grand Final".to_string(),
        round: winners_rounds + 1,
        kind: StageKind::GrandFinal,
        matches: vec![BracketMatch {
            id: "GF-M1".to_string(),
            label: "Grand Final".to_string(),
            round: winners_rounds + 1,
            best_of: 1,
            slots: vec![
                source_slot(1, format!("WB-R{winners_rounds}-M1"), "winner"),
                source_slot(2, format!("LB-R{}-M1", (winners_rounds - 1) * 2), "winner"),
            ],
            advances_to: Vec::new(),
        }],
    });

    Ok(GeneratedBracket {
        tournament_id,
        bracket_type: BracketType::De,
        generated_at: Utc::now(),
        participants,
        stages,
        metadata: BracketMetadata {
            rounds: winners_rounds * 2,
            bracket_size: Some(bracket_size),
            grand_final_reset: true,
            pairing_strategy: Some("seeded_double_elimination".to_string()),
            notes: vec![
                "Winners bracket uses the same seeded layout as single elimination.".to_string(),
                "Losers bracket alternates consolidation rounds and loser injections from the winners bracket.".to_string(),
                "Grand final reset is represented in metadata and should be handled by match orchestration when needed.".to_string(),
            ],
        },
    })
}

fn generate_round_robin(
    tournament_id: Uuid,
    participants: Vec<BracketParticipant>,
) -> GeneratedBracket {
    let schedule = circle_rounds(&participants);
    let round_count = schedule.len();
    let stages = schedule
        .into_iter()
        .enumerate()
        .map(|(index, matches)| BracketStage {
            id: format!("round-robin-round-{}", index + 1),
            label: format!("Round Robin Round {}", index + 1),
            round: index + 1,
            kind: StageKind::RoundRobin,
            matches: matches
                .into_iter()
                .enumerate()
                .map(|(match_index, (left, right))| BracketMatch {
                    id: format!("RR-R{}-M{}", index + 1, match_index + 1),
                    label: format!("Round {} Match {}", index + 1, match_index + 1),
                    round: index + 1,
                    best_of: 1,
                    slots: vec![participant_slot(1, left), participant_slot(2, right)],
                    advances_to: Vec::new(),
                })
                .collect(),
        })
        .collect();

    GeneratedBracket {
        tournament_id,
        bracket_type: BracketType::Rr,
        generated_at: Utc::now(),
        participants,
        stages,
        metadata: BracketMetadata {
            rounds: round_count,
            bracket_size: None,
            grand_final_reset: false,
            pairing_strategy: Some("circle_method_round_robin".to_string()),
            notes: vec![
                "Each team plays every other team exactly once.".to_string(),
                "If the participant count is odd, one bye is inserted into each round.".to_string(),
            ],
        },
    }
}

fn generate_swiss(
    tournament_id: Uuid,
    participants: Vec<BracketParticipant>,
) -> AppResult<GeneratedBracket> {
    if participants.len() < 4 {
        return Err(AppError::Validation(
            "Swiss format requires at least four teams".to_string(),
        ));
    }

    let round_count = ((participants.len() as f64).log2().ceil() as usize + 1).clamp(3, 8);
    let first_round_pairs = swiss_first_round(&participants);
    let mut stages = Vec::with_capacity(round_count);

    stages.push(BracketStage {
        id: "swiss-round-1".to_string(),
        label: "Swiss Round 1".to_string(),
        round: 1,
        kind: StageKind::Swiss,
        matches: first_round_pairs
            .into_iter()
            .enumerate()
            .map(|(match_index, (left, right))| BracketMatch {
                id: format!("SW-R1-M{}", match_index + 1),
                label: format!("Swiss Round 1 Match {}", match_index + 1),
                round: 1,
                best_of: 1,
                slots: vec![participant_slot(1, left), participant_slot(2, right)],
                advances_to: Vec::new(),
            })
            .collect(),
    });

    for round in 2..=round_count {
        stages.push(BracketStage {
            id: format!("swiss-round-{round}"),
            label: format!("Swiss Round {round}"),
            round,
            kind: StageKind::Swiss,
            matches: (0..participants.len().div_ceil(2))
                .map(|match_index| BracketMatch {
                    id: format!("SW-R{round}-M{}", match_index + 1),
                    label: format!("Swiss Round {round} Match {}", match_index + 1),
                    round,
                    best_of: 1,
                    slots: vec![placeholder_score_slot(1), placeholder_score_slot(2)],
                    advances_to: Vec::new(),
                })
                .collect(),
        });
    }

    Ok(GeneratedBracket {
        tournament_id,
        bracket_type: BracketType::Sw,
        generated_at: Utc::now(),
        participants,
        stages,
        metadata: BracketMetadata {
            rounds: round_count,
            bracket_size: None,
            grand_final_reset: false,
            pairing_strategy: Some("score_group_then_buchholz_with_rematch_protection".to_string()),
            notes: vec![
                "Only the first swiss round is deterministic at generation time.".to_string(),
                "Later rounds must be paired by score group, opponent uniqueness, and side-balance constraints.".to_string(),
                "Round count is derived from participant volume to produce enough separation before playoffs."
                    .to_string(),
            ],
        },
    })
}

fn seeded_participants(mut teams: Vec<TournamentTeam>) -> Vec<BracketParticipant> {
    teams.sort_by(|left, right| {
        left.created_at
            .cmp(&right.created_at)
            .then_with(|| left.name.cmp(&right.name))
    });

    teams
        .into_iter()
        .enumerate()
        .map(|(index, team)| BracketParticipant {
            team_id: team.id,
            team_name: team.name,
            seed: index + 1,
        })
        .collect()
}

fn next_power_of_two(value: usize) -> usize {
    if value <= 1 {
        2
    } else {
        value.next_power_of_two()
    }
}

fn standard_seeding(size: usize) -> Vec<usize> {
    let mut seeds = vec![1];
    let mut bracket_size = 1;
    while bracket_size < size {
        bracket_size *= 2;
        let mut next = Vec::with_capacity(bracket_size);
        for seed in &seeds {
            next.push(*seed);
            next.push(bracket_size + 1 - *seed);
        }
        seeds = next;
    }
    seeds
}

fn first_round_slots(
    participants: &[BracketParticipant],
    seeding_positions: &[usize],
) -> Vec<MatchSlot> {
    seeding_positions
        .iter()
        .enumerate()
        .map(|(index, seed)| {
            participants
                .iter()
                .find(|participant| participant.seed == *seed)
                .map_or_else(
                    || MatchSlot {
                        position: (index % 2 + 1) as u8,
                        seed: Some(*seed),
                        team_id: None,
                        team_name: None,
                        source_match_id: None,
                        source_outcome: None,
                        is_bye: true,
                    },
                    |participant| participant_slot((index % 2 + 1) as u8, participant.clone()),
                )
        })
        .collect()
}

fn participant_slot(position: u8, participant: BracketParticipant) -> MatchSlot {
    MatchSlot {
        position,
        seed: Some(participant.seed),
        team_id: Some(participant.team_id),
        team_name: Some(participant.team_name),
        source_match_id: None,
        source_outcome: None,
        is_bye: false,
    }
}

fn source_slot(position: u8, source_match_id: String, outcome: &str) -> MatchSlot {
    MatchSlot {
        position,
        seed: None,
        team_id: None,
        team_name: None,
        source_match_id: Some(source_match_id),
        source_outcome: Some(outcome.to_string()),
        is_bye: false,
    }
}

fn placeholder_score_slot(position: u8) -> MatchSlot {
    MatchSlot {
        position,
        seed: None,
        team_id: None,
        team_name: None,
        source_match_id: None,
        source_outcome: Some("score_group_pairing".to_string()),
        is_bye: false,
    }
}

fn circle_rounds(
    participants: &[BracketParticipant],
) -> Vec<Vec<(BracketParticipant, BracketParticipant)>> {
    let mut rotation = participants.to_vec();
    let bye = if rotation.len() % 2 == 1 {
        Some(BracketParticipant {
            team_id: Uuid::nil(),
            team_name: "BYE".to_string(),
            seed: usize::MAX,
        })
    } else {
        None
    };

    if let Some(bye_participant) = bye {
        rotation.push(bye_participant);
    }

    let rounds = rotation.len().saturating_sub(1);
    let half = rotation.len() / 2;
    let mut result = Vec::with_capacity(rounds);

    for _ in 0..rounds {
        let mut pairings = Vec::new();
        for index in 0..half {
            let left = rotation[index].clone();
            let right = rotation[rotation.len() - 1 - index].clone();
            if left.team_id.is_nil() || right.team_id.is_nil() {
                continue;
            }
            pairings.push((left, right));
        }
        result.push(pairings);

        let mut next = vec![rotation[0].clone()];
        next.push(rotation[rotation.len() - 1].clone());
        next.extend(rotation[1..rotation.len() - 1].iter().cloned());
        rotation = next;
    }

    result
}

fn swiss_first_round(
    participants: &[BracketParticipant],
) -> Vec<(BracketParticipant, BracketParticipant)> {
    let midpoint = participants.len().div_ceil(2);
    let top = participants[..midpoint].to_vec();
    let bottom = participants[midpoint..].to_vec();

    top.into_iter()
        .enumerate()
        .filter_map(|(index, left)| bottom.get(index).cloned().map(|right| (left, right)))
        .collect()
}
