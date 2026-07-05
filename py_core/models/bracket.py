from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
import math


class Bracket(BaseModel):
    def build_bracket(self):
        raise NotImplementedError

    def patch_bracket(self, left: UUID, right: UUID):
        raise NotImplementedError

    pass


class SingleElimMatch(BaseModel):
    team1: Optional[UUID] = None
    team2: Optional[UUID] = None
    winner: Optional[UUID] = None
    match_id: Optional[UUID] = None
    match_number: int = 0
    match_round: int = 0
    next_match: Optional[int] = None

    def add_team(self, team_id: UUID):
        if self.team1:
            if team_id != self.team1 and self.team2 is None:
                self.team2 = team_id
        else:
            self.team1 = team_id


class SingleElim(Bracket):
    teams: list[UUID]
    flat_matches: list[SingleElimMatch] = Field(default_factory=list)

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

    def patch_bracket(self, left: UUID, right: UUID):
        match_left = next(
            x for x in self.flat_matches if x.team1 == left or x.team2 == left
        )
        match_right = next(
            x for x in self.flat_matches if x.team1 == right or x.team2 == right
        )
        if match_left == match_right:
            match_left.team1, match_left.team2 = match_left.team2, match_left.team1
        else:
            if match_left.team1 == left:
                match_left.team1 = right
            elif match_left.team2 == left:
                match_left.team2 = right

            if match_right.team1 == right:
                match_right.team1 = left
            elif match_right.team2 == right:
                match_right.team2 = left

    def _has_active_prev(self, match_number: int):
        return any(
            x
            for x in self.flat_matches
            if x.next_match == match_number and x.winner is None
        )

    def _iterate(self):
        for x in self.flat_matches:
            if x.winner:
                continue
            if x.team1 and not x.team2:
                self._set_winner(x.team1)

        return self.flat_matches

    def set_winner(self, team_id: UUID | None):
        if not team_id:
            return
        cur_m = next(
            (
                x
                for x in self.flat_matches
                if x.winner is None and (x.team1 == team_id or x.team2 == team_id)
            ),
            None,
        )
        if not cur_m:
            return
        if self._has_active_prev(cur_m.match_number):
            return
        cur_m.winner = team_id
        if cur_m and cur_m.next_match:
            next_m = self.flat_matches[cur_m.next_match]
            next_m.add_team(cur_m.winner)
            print()
            print(
                f"Winner of match {cur_m.match_number} is {cur_m.winner}",
                f"Next match is {next_m.match_number} {cur_m.next_match}",
            )
        self._iterate()
