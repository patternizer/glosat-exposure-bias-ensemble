# glosat-exposure-bias-ensemble

Python algorithm to merge exposure bias model estimates from Emily Wallis with HadCRUT5 exposure bias ensemble realisations and exposure change breakpoints into Ruptures changepoint lists for LEK processing

## Contents

* `exposure-bias-model-reader.py` - reads in exposure bias model estimates by Emily Wallis for bias-corrected station input to LEK processing chain 
* `exposure-bias-model-writer-processed.py` - writes exposure bias model estimates per station in CRUTEM format ( single merged file ) - processed stations only
* `exposure-bias-model-writer.py` - writes exposure bias model estimates per station in CRUTEM format ( single merged file ) - all CRUTEM5
* `exposure-bias-model-uncertainty-writer.py` - writes exposure bias model uncertainty estimates (95% c.i.) per station in CRUTEM format ( single merged file ) - all CRUTRM6
* `exposure-bias-hadcrut5.py` - n-member ensemble from 1000000 realisations of the HadCRUT5 exposure bias model (applied to all stations at latitude level)
* `exposure-bias-hadcrut5-runnable.py` - 10-member equiprobable ensemble from 1000000 realisations of the HadCRUT5 exposure bias model (applied to all stations at latitude level)
* `exposure-bias-hadcrut5-runnable-per-station.py` - 10-member equiprobable ensemble from 1000000 realisations of the HadCRUT5 exposure bias model (applied to stations individually)
* `exposure-bias-metadata-reader.py` - reads in spreadsheet of exposure metadata and computes breakpoints for breakpoint input to LEK processing chain

The first step is to clone the latest glosat-exposure-bias-ensemble code and step into the check out directory: 

    $ git clone https://github.com/patternizer/glosat-exposure-bias-ensemble.git
    $ cd glosat-exposure-bias-ensemble

### Usage

The code was tested locally in a Python 3.8.11 virtual environment.
  
## License

The code is distributed under terms and conditions of the [Open Government License](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Contact information

* [Michael Taylor](michael.a.taylor@uea.ac.uk)



