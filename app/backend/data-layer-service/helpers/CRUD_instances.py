from models.CRUD import CRUD
from models.data_managers.MongoManager import MongoManager
from models.data_managers.DragonManager import DragonManager
from shared.user_service.models.User import User
from models.DataManager import DataManager


class MongoUserManager(MongoManager[User]):
    _model_class = User


class DragonUserManager(DragonManager[User]):
    _model_class = User


user_data_manager = DataManager(db=MongoUserManager, cache=DragonUserManager)
user_crud = CRUD(data_manager=user_data_manager, model=User)
