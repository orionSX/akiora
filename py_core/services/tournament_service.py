from models.tournament import Tournament, PlayerJoinRequest
from models.enums import Server, GameStatus, HostStatus, VerificationRequest, PoolStatus
from models.vos import EloCard, TournamentSettings, LeagueAccount
from uuid import UUID
from services.host_service import HostService
from services.user_service import UserService
from models.bracket import SingleElim
from typing import Optional


class TournamentService:
    def __init__(self, host_service: HostService, user_service: UserService):
        self._host_service = host_service

    async def get_by_id(self, id: str | UUID):

        return await Tournament.get(id)

    async def get_all(self):
        return await Tournament.find().to_list()

    async def get_by_host(self, host_id: UUID):
        return await Tournament.find_many(Tournament.host_id == host_id).to_list()

    async def get_by_server(self, server: Server):
        return await Tournament.find_many(Tournament.server == server).to_list()

    async def get_by_status(self, status: GameStatus):
        return await Tournament.find_many(Tournament.status == status).to_list()

    async def create(self, patch: dict, user_id: str):
        meta = await self._host_service.get_active_by_uid(user_id)
        if not meta:
            raise ValueError("Host was not found")
        ts = TournamentSettings(**patch)
        if not ts.draft_settings and not ts.presign_settings:
            raise ValueError(
                "Either draft_settings or presign_settings must be provided."
            )
        tournament = Tournament(host_id=meta.id, settings=ts)
        await tournament.save()
        return tournament

    async def add_to_pending_draft_pool(self, tourn_id: str, patch: dict):
        tourn = await self.get_by_id(tourn_id)

        tourn.pool.add_pending_user(patch)
        await tourn.save()

    async def update_pool_card(
        self, tourn_id: str, player_id: str, user_id: str, patch: dict
    ):
        tourn = await self.get_by_id(tourn_id)

        tourn.pool.update_pool_player(player_id=player_id, patch=patch)
        await tourn.save()

    async def patch_draft_captains(self, tourn_id: str, actor_id: UUID, patch: dict):
        tourn = await self.get_by_id(tourn_id)
        tourn.pool.patch_captains(patch.get("remove"), patch.get("append"))
        await tourn.save()

    async def add_to_team(
        self, tourn_id: str, player_id: str, actor_id: UUID, patch: dict
    ):
        tourn = await self.get_by_id(tourn_id)
        tourn.pool.add_to_team(player_id=UUID(player_id), captain_id=actor_id)
        await tourn.save()

    async def prebuild_bracket(self, tourn_id: str, actor_id: UUID):
        tourn = await self.get_by_id(tourn_id)
        tourn.bracket = SingleElim(teams=[x.id for x in tourn.pool.teams])
        tourn.bracket.build_bracket()
        await tourn.save()

    async def patch_bracket(self, tourn_id: str, actor_id: UUID, patch: dict):
        tourn = await self.get_by_id(tourn_id)
        tourn.bracket.patch_bracket(UUID(patch.get("left")), UUID(patch.get("right")))
        await tourn.save()

    async def add_to_accepted_draft_pool(self, tourn_id: str, player_id: str):
        tourn = await self.get_by_id(tourn_id)
        player = await self._user_service.get_by_id(player_id)
        elocard = self._calc_elo(player.league_accounts)
        tourn.pool.add_accepted_user(player_id=player_id, elo_card=elocard)
        await tourn.save()

    async def close_pool(self, tourn_id: str, player_id: str):
        tourn = await self.get_by_id(tourn_id)
        tourn.pool.status = PoolStatus.CLOSED
        await tourn.save()

    def _calc_elo(self, accs: list[LeagueAccount]) -> EloCard:
        ru = [
            x
            for x in accs
            if x.status == VerificationRequest.VERIFIED and x.server == Server.RU
        ]
        ru_card: Optional[EloCard] = None
        euw_card: Optional[EloCard] = None
        best_ru: Optional[LeagueAccount] = None
        for i in range(len(ru) - 1):
            best_ru = LeagueAccount.get_best(ru[i], ru[i + 1])
        if best_ru:
            ru_card = EloCard(
                tier=best_ru.tier,
                value=best_ru.elo,
            )
        euw = [
            x
            for x in accs
            if x.status == VerificationRequest.VERIFIED and x.server == Server.EUW
        ]
        best_euw: Optional[LeagueAccount] = None
        for i in range(len(euw) - 1):
            best_euw = LeagueAccount.get_best(euw[i], euw[i + 1])

        if best_euw:
            euw_card = EloCard(
                tier=best_euw.tier,
                value=best_euw.elo,
            )
        if ru_card:
            if euw_card:
                if euw_card.total >= ru_card.total:
                    return euw_card
            return ru_card
        elif euw_card:
            return euw_card
        return EloCard()
