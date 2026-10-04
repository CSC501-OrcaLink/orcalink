# Data Sources

This document 

## The Whale Museum
- Received historical sighting records.
- Records include dates, locations, reported whale groups, and source codes.
- The dataset does not provide individual whale IDs.
- These records can support analysis of reported group presence, but cannot directly establish individual co-sighting.
- Data sharing is subject to the release agreement

## Dryad
- Available files contain J-pod observations and lifespan information.
- Observation records include whale IDs, sighting IDs, timestamps, coordinates, and observation flags.
- Some IDs were assigned based on reports of whole pods or matrilines.
- Missing IDs and uncertain identification need to be considered during preprocessing.
- The data does not provide complete individual encounter coverage for J, K, and L pods.

## Center for Whale Research
- Public identification records can help describe whale identities and family relationships.
- Additional encounter information has been requested by email.
- We are waiting for a response about the available records.

## Preprocessing (Current)
- Check missing values and repeated records.
- Compare whale IDs across files.
- Check observation dates against lifespan records.
- Document how identification and observation flags should be interpreted.
- Keep source information when preparing records for model.

## Information still needed
- Individual encounter records on J, K, and L pods.
- Maternal relationships with supporting sources.
- Explanations of source code and uncertain identification.
- Confirmation of how each dataset may be used and shared. 
