"""The engine hook: every number on the model page comes from simulate(). Default: SFM's engine on the spec after
custom.adjust(). Change anything, even replace it with your own logic, but return the same form as SFM's engine:
{name: array of shape (reps, steps)} for every stock (and 'stock@end'), flow and outside factor of the spec, plus
'_theta' (the parameter draws) when the spec has parameter uncertainty."""
from sfm import runner

from . import custom


def simulate(spec, scenario, reps, seed):
    return runner.simulate(custom.adjust(spec), scenario, reps, seed)
