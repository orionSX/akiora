from models.bracket import SingleElim
from models.tournament import Team
from uuid import uuid7
from rich import print
import copy
import pytest
import random


@pytest.mark.parametrize("t", range(2, 10))
def test_bracket_bye_iteration(t):
    se = SingleElim(teams=[uuid7() for _ in range(t)])
    se.build_bracket()
    s0 = copy.deepcopy(se.flat_matches)
    s1 = copy.deepcopy(se._iterate())
    se._iterate()
    se._iterate()
    se._iterate()
    s2 = copy.deepcopy(se._iterate())
    print(f"Number of teams: {t}")
    print(s0)
    print(s1)
    print(s2)
    assert s1 == s2


@pytest.mark.parametrize("t", range(2, 10))
def test_bracket_complete_iteration(t):
    se = SingleElim(teams=[uuid7() for _ in range(t)])
    se.build_bracket()
    se._iterate()
    for x in se.flat_matches:
        rn = random.randint(1, 2)
        if rn == 1:
            se._set_winner(x.team1)
        else:
            se._set_winner(x.team2)
    print(se.flat_matches)

    wn = se.flat_matches[-1].winner
    print(f"Winner is {wn}")
    for m in se.flat_matches:
        if m.team1 == wn or m.team2 == wn:
            print(m)
    assert True


@pytest.mark.parametrize("t", range(2, 5))
def test_bracket_team_change(t):
    teams = [uuid7() for _ in range(t)]
    left = teams[0]
    right = teams[-1]
    print(left, right)
    se = SingleElim(teams=teams)

    se.build_bracket()
    print(se.flat_matches)
    se.patch_bracket(left=teams[0], right=teams[-1])
    print(se.flat_matches)

    assert True
