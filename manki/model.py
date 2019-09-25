import genanki

MODEL_NAME = "manki model"
MODEL = genanki.Model(
    genanki.guid_for(MODEL_NAME),
    MODEL_NAME,
    fields=[
        # three fields: a question, an answer, a context tag
        {"name": "Question"},
        {"name": "Answer"},
        {"name": "Context"},
    ],
    templates=[
        # add a single card, which displays
        # the "Question", prefixed by the "Context" field as the question
        # the "Question" a horizontal ruler and the "Answer" as the answer
        {
            "name": "Card 1",
            "qfmt": "{{#Context}}{{Context}}: {{/Context}}{{Question}}",
            "afmt": "{{FrontSide}}<hr id=\"answer\">{{Answer}}",
        }
    ],
    # standard css for cards generated from this note, will be added by the cli
    css="",
)

# TODO be able to set via CLI
DECK_NAME = "manki flashcards"
DECK = genanki.Deck(hash(DECK_NAME), DECK_NAME)
