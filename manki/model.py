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
    # standard css for cards generated from this note
    # TODO allow adding additional css via cli option
    css="""
        .card {
            font-family: 'Crimson Pro', 'Crimson Text', 'Cardo', 'Times', 'serif';
            text-align: center;
            color: black;
            background-color: white;
        }
        """,
)


# custom note that uses only the question field for guid generation
# instead of all fields by default
# TODO maybe the id should actually not be based on the html question but
# rather on the original markdown question (less likely to change)
class FirstFieldGUIDNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


DECK_NAME = "manki flashcards"
# TODO guid based on deck name? hash to int?
DECK = genanki.Deck(123, DECK_NAME)
