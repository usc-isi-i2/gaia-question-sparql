# question-sparql
[gaia] convert a xml question to sparql query, and relax the question when no results/wrong results returned

## Documentation

#### Installation:
* `git clone` the repo
* run `cd question-sparql`
* run `pip install -r requirements.txt` to install dependencies

#### Examples:

* try examples with `python examples/try.py`


#### Relax Strategies:
First, try to query with strictly translated SPARQL query. If there is no result, query with the following relax strategies until non-empty results returned.
* wider_range:
  * change the specified start/end char index to a range. (from 'equal to' to 'less than'/'greater than')
  * e. g. 
  ```
    ...
    ?var0 aida:startOffset 169 .
    ?var0 aida:endOffsetInclusive 185 .
    ...
  ``` 
  will be replaced by
  ```
    ...
    ?var0 aida:startOffset ?startOffset .
    ?var0 aida:endOffsetInclusive ?endOffsetInclusive .
    FILTER( ?startOffset <= 170 || ?endOffsetInclusive >= 180 )
    ...
  
  ```
  
 * larger_bound:
    * change the specified coordinate of images/videos to a range. (from 'equal to' to 'less than'/'greater than')
    * e. g. 
    ```
    ...
    ?var1 aida:boundingBoxUpperLeftX 20 .
    ?var1 aida:boundingBoxUpperLeftY 20 .
    ?var1 aida:boundingBoxLowerRightX 50 .
    ?var1 aida:boundingBoxLowerRightY 50 .
    ...
    ``` 
    will be replaced by
    ```
    ...
    ?var1 aida:boundingBoxUpperLeftX ?boundingBoxUpperLeftX .
    ?var1 aida:boundingBoxUpperLeftY ?boundingBoxUpperLeftY .
    ?var1 aida:boundingBoxLowerRightX ?boundingBoxLowerRightX .
    ?var1 aida:boundingBoxLowerRightY ?boundingBoxLowerRightY .
    FILTER( ?boundingBoxUpperLeftX <= 20 || ?boundingBoxUpperLeftY <= 20 || ?boundingBoxLowerRightX >= 50 || ?boundingBoxLowerRightY >= 50 )
    ...
    
    ```
  
 * ignore_enttype:
    * remove specified `enttype`
    * e.g.
    ```
    {
        ?target skos:prefLabel "Mezhigorie" .
        ?target rdf:type ldcOnt:Vehicle .
    } UNION {
        ?target aida:justifiedBy ?var0 .
        ?target rdf:type ldcOnt:Vehicle .
        ?var0 a aida:TextJustification .
        ...   
    } UNION {
        ?target aida:justifiedBy ?var0 .
        ?target rdf:type ldcOnt:Vehicle .
        ?var0 a aida:VideoJustification .
        ...
    }

    ```
    will be 
    
    ```
    {
        ?target skos:prefLabel "Mezhigorie" .  
    } UNION {
        ?target aida:justifiedBy ?var0 .
        ?var0 a aida:TextJustification .
        ...  
    } UNION {
        ?target aida:justifiedBy ?var0 .
        ?var0 a aida:VideoJustification .
        ...
    }

