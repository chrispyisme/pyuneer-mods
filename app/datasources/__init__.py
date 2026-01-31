"""app.datasources package init"""
from app.datasources.abstract import AbstractDatasource
from app.datasources.json_datasource import JsonDatasource
from app.datasources.db_datasource import DBDatasource
from app.datasources.file_datasource import FileDatasource
from app.datasources.contracts import CrudInterface, DatasourceInterface

__all__ = [
    "AbstractDatasource",
    "JsonDatasource",
    "DBDatasource",
    "FileDatasource",
    "CrudInterface",
    "DatasourceInterface"
]
