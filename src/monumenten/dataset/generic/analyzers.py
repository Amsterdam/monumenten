import elasticsearch_dsl as es
from elasticsearch_dsl import analysis

synonym_filter = analysis.token_filter(
    'synonyms',
    type='synonym',
    synonyms=[
        '1e=>eerste',
        '2e=>tweede',
        '3e=>derde',
        '4e=>vierde',
    ]
)

# Added to display_naam  for https://taiga.datapunt.amsterdam.nl/project/kpaska-datapunt-backend/us/1397
# display_naam can be prefixed with 'gelegen bij', 'betreden via' of 'gelegen tegenover'
noname_prefix_filter = analysis.token_filter(
    'noname_prefix',
    type='stop',
    stopwords=[
        "betreden",
        "via",
        "gelegen",
        "bij"
    ]
)

naam_stripper = analysis.char_filter(
    'naam_stripper',
    type='mapping',
    mappings=[
        "-=>' '",  # change '-' to separator
        ".=>' '",  # change '.' to separator
    ]
)

monument_naam = es.analyzer(
    'monument_naam',
    tokenizer='standard',
    filter=['lowercase', 'trim', 'asciifolding', synonym_filter, noname_prefix_filter],
    char_filter=[naam_stripper],

)

complex_naam = es.analyzer(
    'complex_naam',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[naam_stripper],
)

subtype = es.analyzer(
    'subtype',
    tokenizer='keyword',
    filter=['lowercase'],
)