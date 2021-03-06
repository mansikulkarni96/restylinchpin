from abc import ABC, abstractmethod


class BaseDB(ABC):

    @abstractmethod
    def db_insert(self, identity, name, status):
        return

    @abstractmethod
    def db_insert_no_name(self, identity, status):
        return

    @abstractmethod
    def db_search(self, name):
        return

    @abstractmethod
    def db_update(self, identity, status):
        pass

    @abstractmethod
    def db_remove(self, identity):
        pass

    @abstractmethod
    def db_list_all(self):
        pass
