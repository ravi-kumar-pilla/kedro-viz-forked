import pytest
from kedro.io.data_catalog import DataCatalog

from kedro_viz.data_access.repositories import CatalogRepository


class TestDataCatalogRepository:
    def test_get_layer_mapping_for_transcoded_dataset(self):
        repo = CatalogRepository()
        catalog_config = {
            "cars@pandas": {
                "type": "pandas.CSVDataSet",
                "filepath": "cars.csv",
                "layer": "raw",
            },
        }
        catalog = DataCatalog.from_config(catalog_config)
        repo.set_catalog(catalog)
        assert repo.get_layer_for_dataset("cars") == "raw"
        assert repo.get_layer_for_dataset("cars@pandas") == "raw"

    def test_validate_layers_error(self):
        repo = CatalogRepository()
        catalog_config = {
            "car@pandas1": {
                "type": "pandas.CSVDataSet",
                "filepath": "cars.csv",
                "metadata": {
                    "kedro-viz": {
                        "layer": "raw",
                    },
                },
            },
            "car@pandas2": {
                "type": "pandas.ParquetDataSet",
                "filepath": "cars.pq",
                "metadata": {
                    "kedro-viz": {
                        "layer": "intermediate",
                    },
                },
            },
        }
        catalog = DataCatalog.from_config(catalog_config)
        repo.set_catalog(catalog)
        with pytest.raises(
            ValueError,
            match=r"Transcoded datasets should have the same layer. "
            "Please ensure consistent layering in your Kedro catalog. "
            "Mismatch found for: ",
        ):
            repo.get_layer_for_dataset("car@pandas1")

    def test_get_layer_mapping_from_metadata(self):
        repo = CatalogRepository()
        catalog_config = {
            "car@pandas1": {
                "type": "pandas.CSVDataSet",
                "filepath": "cars.csv",
                "metadata": {
                    "kedro-viz": {
                        "layer": "raw",
                    },
                },
            },
        }
        catalog = DataCatalog.from_config(catalog_config)
        repo.set_catalog(catalog)
        assert repo.get_layer_for_dataset("car") == "raw"

    # TODO : Update test after Kedro 19 release.
    def test_get_layer_mapping_from_metadata_and_top_level_layer(self):
        repo = CatalogRepository()
        catalog_config = {
            "car_1": {
                "type": "pandas.CSVDataSet",
                "filepath": "cars.csv",
                "metadata": {
                    "kedro-viz": {
                        "layer": "raw",
                    },
                },
            },
            "car_2": {
                "type": "pandas.CSVDataSet",
                "filepath": "cars.csv",
                "layer": "raw",
            },
        }
        catalog = DataCatalog.from_config(catalog_config)
        repo.set_catalog(catalog)
        assert repo.get_layer_for_dataset("car_1") == "raw"
        assert repo.get_layer_for_dataset("car_2") == "raw"
