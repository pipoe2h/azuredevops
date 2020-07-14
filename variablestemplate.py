from calm.dsl.builtins import CalmVariable as Variable

ENVIRONMENT = Variable.WithOptions.Predefined.string(
    ["DEV", "PROD"], default="DEV", is_mandatory=True, runtime=True
)