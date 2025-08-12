from models.CRUD import CRUD
from models.data_managers.MongoManager import MongoManager
from models.data_managers.DragonManager import DragonManager
from models.user_service.User import User


class MongoUserManager(MongoManager[User]):
    _model_class = User


class DragonUserManager(DragonManager[User]):
    _model_class = User


user_crud = CRUD(data_managers=[MongoUserManager, DragonUserManager], model=User)
