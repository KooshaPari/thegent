# thegent Nix package - buildPythonApplication from flake source
{ python3, lib }:
{ src }:
python3.pkgs.buildPythonApplication rec {
  pname = "thegent";
  version = "0.1.0";
  inherit src;
  format = "pyproject";
  nativeBuildInputs = with python3.pkgs; [ hatchling hatch-vcs ];
  propagatedBuildInputs = with python3.pkgs; [
    httpx
    typer
    rich
    pydantic
    pydantic-settings
    python-dotenv
    tenacity
    pyyaml
    ruamel-yaml
    fastmcp
    starlette
    uvicorn
    granian
    orjson
    cachetools
    diskcache
    watchdog
    watchfiles
    fastjsonschema
    psutil
    pybreaker
    textual
    tomlkit
    tomli
    rtoml
    litellm
    opentelemetry-api
    opentelemetry-sdk
  ];
  doCheck = false;
  meta = with lib; {
    description = "Unified agent orchestration CLI for Factory skills, droids, and multi-agent workflows";
    homepage = "https://github.com/kooshapari/thegent";
    license = licenses.mit;
    mainProgram = "thegent";
  };
}
