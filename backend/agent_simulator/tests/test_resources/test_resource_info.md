# Info
This flder includes different static files and similar that is currently used for running tests.
Some of these files are simply there to load a SimulationConfig (no need to run a discovery, (saves time)).
Others are there for actual testing. This should be looked into since some of these files & tests are really outdated
and should probibaly be looked into.

# Wierd behaviour that is done
When tests are ran on the git pipeline, the entire test_resources folder is copied to another newly created folder called pickle_resources,
this folder, the docker? runnigh the tests is owner and has all read/write acces. This was done because initially all tests were ran as root
on the pipeline, this was changed and tests were no longer ran as root for security reasons. This newly created folder (gets created & removed each pipline)
solved that problem. (Some tests needs to write to a file, which was not allowed when changed form root to non-root user). 
You that write or run tests as a student next year (2026) does not need to take this into consideration, it is more of a git & docker issue 
(should not be an issue as of now though).