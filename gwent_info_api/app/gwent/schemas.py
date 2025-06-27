from typing import Optional
from pydantic import BaseModel, Field, RootModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class RankingInfoRankProgressionSchema(BaseSchema):
    mosaic_piece_count: int
    rank: int


class FactionProgressionsItemSchema(BaseSchema):
    is_used_for_score_calculation: bool
    unlocked_score: int
    real_score: int
    real_score_peak: int
    games_count: int
    unlocked_score_games_count_threshold: int
    unlocked_score_fraction: float



class RankingInfoFactionProgressionsSchema(BaseSchema):
    faction: str
    faction_progression: FactionProgressionsItemSchema


class FactionGamesStatsItemSchema(BaseSchema):
    wins_count: int
    losses_count: int
    draws_count: int
    games_count: int


class RankingInfoFactionGamesStatsSchema(BaseSchema):
    faction: str
    faction_games_stats: FactionGamesStatsItemSchema


class RankingInfoRatingSchema(BaseSchema):
    score: int


class RankingInfoParagonSchema(BaseSchema):
    paragon_level: int
    player_level: int


class RankingInfoRequirementParamsSchema(BaseSchema):
    status: str


class RankingInfoRequirementSchema(BaseSchema):
    type: str
    params: RankingInfoRequirementParamsSchema


class RankingInfoVanitySchema(BaseSchema):
    category: str
    item_definition_id: str


class FullUserRankingInfoSchema(BaseSchema):
    id: str
    username: str
    platform: str
    title: str
    score: int
    position: int
    continental_position: int
    rank_id: int
    leaderboard: str
    data_score_updated: Optional[str] = None
    data_level_updated: Optional[str] = None
    date_created: str
    wins_count: int
    losses_count: int
    draws_count: int
    games_count: int
    level: int
    continent: str
    country: str
    rank_progression: RankingInfoRankProgressionSchema
    faction_progressions: list[RankingInfoFactionProgressionsSchema]
    faction_games_stats: list[RankingInfoFactionGamesStatsSchema]
    rating: RankingInfoRatingSchema
    paragon: RankingInfoParagonSchema
    requirements: list[RankingInfoRequirementSchema]
    vanities: list[RankingInfoVanitySchema] | None = None


class ProfileDataProgressBarSchema(BaseSchema):
    level: int
    crown_pieces: int


class ProfileDataAccomplishmentSchema(BaseSchema):
    id: str
    type: str


class ProfileDataStatsWinsSchema(BaseSchema):
    Monster: int
    Nilfgaard: int
    NorthernKingdom: int
    Scoiatael: int
    Skellige: int
    Syndicate: int


class ProfileDataStatsSchema(BaseSchema):
    wins: ProfileDataStatsWinsSchema
    ggs_sent_count: int
    ggs_received_count: int
    pro_ladder_score_monster: int
    pro_ladder_score_nilfgaard: int
    pro_ladder_score_northern_kingdom: int
    pro_ladder_score_scoiatael: int
    pro_ladder_score_skellige: int
    pro_ladder_score_syndicate: int
    pro_ladder_games_monster: int
    pro_ladder_games_nilfgaard: int
    pro_ladder_games_northern_kingdom: int
    pro_ladder_games_scoiatael: int
    pro_ladder_games_skellige: int
    pro_ladder_games_syndicate: int


class ProfileDataParagonSchema(BaseSchema):
    paragon_level: int
    player_level: int
    current_level_experience: int
    next_level_required_experience: int


class FullProfileDataSchema(BaseSchema):
    id: str
    progress_bar: ProfileDataProgressBarSchema
    accomplishments: list[ProfileDataAccomplishmentSchema]
    stats: ProfileDataStatsSchema
    public_profile_hidden: bool
    platform: str
    paragon: ProfileDataParagonSchema


class GwentSitePlayerInfoSchema(BaseSchema):
    place: int
    country: str
    nickname: str
    matches: str
    mmr: str


class RanksThresholdSchema(BaseSchema):
    rank8: GwentSitePlayerInfoSchema
    rank32: GwentSitePlayerInfoSchema
    rank200: GwentSitePlayerInfoSchema
    rank500: GwentSitePlayerInfoSchema


class CardSetItemSchema(BaseSchema):
    Neutral: int
    Monster: int
    Nilfgaard: int
    NorthernKingdom: int
    Scoiatael: int
    Skellige: int
    Syndicate: int


class CardSetSchema(BaseSchema):
    non_premium: CardSetItemSchema
    premium: CardSetItemSchema
    any: CardSetItemSchema


class CardCollectionSchema(BaseSchema):
    BaseSet: CardSetSchema
    AllCards: CardSetSchema
    Campaign1: CardSetSchema
    Expansion1: CardSetSchema
    Expansion2: CardSetSchema
    Expansion3: CardSetSchema
    Expansion4: CardSetSchema
    Expansion5: CardSetSchema
    Expansion6: CardSetSchema
    Expansion7: CardSetSchema
    Expansion8: CardSetSchema


class CardDefinitionSchema(BaseSchema):
    id: str


class FavouriteCardItem(BaseSchema):
    card_definition: CardDefinitionSchema


class FullDeckInfoSchema(BaseSchema):
    collection: CardCollectionSchema
    full_collection: CardCollectionSchema
    favourite_card: FavouriteCardItem
    favourite_faction: str


class ProfileImageSchema(BaseSchema):
    avatar_url: Optional[str] = None
    border_url: Optional[str] = None
