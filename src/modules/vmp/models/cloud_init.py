from pydantic import BaseModel, Extra, Field


class NoCloud(BaseModel, extra=Extra.forbid):
    class Data(BaseModel, extra=Extra.forbid):
        metaData: dict | str = Field({}, alias="meta-data")
        userData: dict | str = Field({}, alias="user-data")
        vendorData: dict | str | None = Field(None, alias="vendor-data")
        networkConfig: dict | str | None = Field(None, alias="network-config")

    class Seed(BaseModel, extra=Extra.forbid):
        path: str

    data: Data
    seed: Seed
