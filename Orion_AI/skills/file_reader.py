from Core.Agent.schemas import Observation
def file_read(args: dict)-> Observation:
    path = args.get("path")
    if path is None:
        return Observation(
            success= False,
            tool= "file_read",
            data = None,
            error = "File path not provided or does not exist",
        )
    try:
        with open(path, "r", encoding="utf-8") as f:
            contents = f.read()
        return Observation(
            success = True,
            tool= "file_read",
            data = contents,
            error = None,
        )
    except Exception as e:
        return Observation(
            success= False,
            tool= "file_read",
            data= None,
            error = str(e),
        )
                          # no path    → expect success=False + "no path" message