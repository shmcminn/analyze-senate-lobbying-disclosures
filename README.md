# Analyzing Senate lobbying disclosures

The U.S. Senate posts lobbyist disclosure spending data in XML format, which is due quarterly, [here](https://www.senate.gov/legislative/Public_Disclosure/database_download.htm). It includes lobbying in both the House of Representatives and Senate.

Those Senate files are broken up chronologically, with (I believe) 1,000 entries per file.

This Python script looks for a folder of those XML files in your local directory, combines them, filters them on categories such as year/filing period/lobbying topic, then exports the results as a CSV file.

This was originally built for CQ Roll Call reporting on banking and fiancial institutions lobbying data, though obviously it has broader uses.