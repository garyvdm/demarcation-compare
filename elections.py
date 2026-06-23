from pydantic import BaseModel, ConfigDict, Field, RootModel, computed_field


class Elections(RootModel[list["Election"]]): ...


class Election(BaseModel):
    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})

    title: str
    sub_elections: list["SubElection"] = Field(default_factory=list)

    @computed_field
    @property
    def slug(self) -> str:
        return self.title.partition(" ")[0]


class SubElection(BaseModel):
    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})

    title: str

    @computed_field
    @property
    def slug(self) -> str:
        return self.title.lower()


elections = Elections(
    [
        Election(
            title="2000 Municipal",
            sub_elections=[
                SubElection(title="District"),
                SubElection(title="Local"),
            ],
        ),
        Election(
            title="2004 General",
            sub_elections=[
                SubElection(title="National"),
                SubElection(title="Provincial"),
            ],
        ),
        Election(
            title="2006 Municipal",
            sub_elections=[
                SubElection(title="District"),
                SubElection(title="Local"),
            ],
        ),
        Election(
            title="2009 General",
            sub_elections=[
                SubElection(title="National"),
                SubElection(title="Provincial"),
            ],
        ),
        Election(
            title="2011 Municipal",
            sub_elections=[
                SubElection(title="District"),
                SubElection(title="Local"),
            ],
        ),
        Election(
            title="2014 General",
            sub_elections=[
                SubElection(title="National"),
                SubElection(title="Provincial"),
            ],
        ),
        Election(
            title="2016 Municipal",
            sub_elections=[
                SubElection(title="District"),
                SubElection(title="Local"),
            ],
        ),
        Election(
            title="2019 General",
            sub_elections=[
                SubElection(title="National"),
                SubElection(title="Provincial"),
            ],
        ),
        Election(
            title="2021 Municipal",
            sub_elections=[
                SubElection(title="District"),
                SubElection(title="Local"),
            ],
        ),
        Election(
            title="2024 General",
            sub_elections=[
                SubElection(title="National"),
                SubElection(title="Provincial"),
                # TODO add the new one
            ],
        ),
        Election(
            title="2026 Municipal",
            sub_elections=[
                SubElection(title="District"),
                SubElection(title="Local"),
            ],
        ),
    ]
)


if __name__ == "__main__":
    from pathlib import Path
    from subprocess import run, PIPE
    from json import dumps
    from pydantic.json_schema import models_json_schema

    path = Path("data/elections.json")
    print(f"Writing {path} ...")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(elections.model_dump_json())

    ts_path = Path("web/elections.ts")
    print(f"Writing {ts_path} ...")
    ts_path.parent.mkdir(parents=True, exist_ok=True)
    schema = models_json_schema([(Elections, "serialization")])[1]
    for item in schema["$defs"].values():
        for property in item.get("properties", {}).values():
            property.pop("title")

    # print(schema)
    run(
        [
            "npx",
            "--package=json-schema-to-typescript",
            "json2ts",
            "--unreachableDefinitions",
            "--output",
            ts_path,
        ],
        input=dumps(schema),
        text=True,
        stdout=PIPE,
    )
