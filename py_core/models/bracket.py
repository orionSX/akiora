from pydantic import BaseModel
from uuid import UUID
from typing import Optional
import math


class SingleElimMatch(BaseModel):
    team1: Optional[UUID] = None
    team2: Optional[UUID] = None
    winner: Optional[UUID] = None
    match_id: Optional[UUID] = None
    match_number: int = 0
    match_round: int = 0
    next_match: Optional[int] = None


class SingleElim(BaseModel):
    teams: list[UUID]
    flat_matches: list[SingleElimMatch] = []

    def build_bracket(self):
        n_teams = len(self.teams)
        if n_teams < 2:
            raise ValueError
        n_rounds = math.ceil(math.log2(n_teams))
        total_slots = 2**n_rounds

        rounds: list[list[SingleElimMatch]] = []
        first_round_matches: list[SingleElimMatch] = []

        for match_idx in range(total_slots // 2):
            match = SingleElimMatch(match_round=0, match_number=match_idx)
            first_round_matches.append(match)

        for team_idx in range(n_teams):
            if team_idx < total_slots // 2:
                first_round_matches[team_idx].team1 = self.teams[team_idx]
            else:
                match_index = team_idx - (total_slots // 2)
                first_round_matches[match_index].team2 = self.teams[team_idx]

        rounds.append(first_round_matches)

        current_round_matches = first_round_matches
        current_round_number = 0
        matches_in_round = total_slots // 2

        while matches_in_round > 1:
            next_round_number = current_round_number + 1
            match_offset = current_round_matches[-1].match_number + 1
            next_round_matches: list[SingleElimMatch] = []
            matches_in_round //= 2

            for match_idx in range(matches_in_round):
                match = SingleElimMatch(
                    match_round=next_round_number,
                    match_number=match_idx + match_offset,
                )
                next_round_matches.append(match)

            for match_idx, current_match in enumerate(current_round_matches):
                next_match_idx = match_idx // 2

                current_match.next_match = next_match_idx + match_offset

            rounds.append(next_round_matches)
            current_round_matches = next_round_matches
            current_round_number = next_round_number

        flat_matches = []
        for x in rounds:
            flat_matches.extend(x)
        self.flat_matches = flat_matches
        return self.flat_matches
