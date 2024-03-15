July 19 2019
These Intermediate CA Certificates should be added to any default trust stores on BMW Group systems.
This will provide compatibility if they are needed to chain to a root of trust used at BMW Group.
This should be in addition to any default trust stores that may already be installed by your platform
Please be sure all base images, containers, application deployments contain these in the trust store at a minimum.
They are in PEM format for easy addition to stores.
The .CRT extension can be changed to .cer or .pem if desired without impact.
The .CRT and .CER are both recognized by the Microsoft OS and can be installed or opened easily.