# manki

A cli tool to convert and bundle markdown notes into an anki package.

## Example

```bash
manki ~/notes/
```

## Documentation

### Note Discovery

### Markdown Notes Format

### Note id

Every note needs to have a unique id. This is required, because Anki uses the id to check for existing notes when importing a package. If, when importing a package, some note id already exists, it will get updated with the new information.

`manki` uses a hash of the first field (the question) as the note id. So, as long as the question does not change, the note will be able to get matched with the existing Anki note on import. If you ever want to change the question you need to delete the old question (TODO link Delete) and add the changed question as a new note.

This behavior was chosen because it works for me. Questions seldom change, other fields much more frequently. And if I want to change a question then it's a good workflow that this results in deleting the old and creating a new note (breaking the review history of the cards associated with that note).

### Update

You will be able to update an existing note as long as the note id has not changed. Thus, any field except for the question field can be changed in your markdown notes and it will update the existing Anki note on the next import.

### Delete

The Anki package import does not handle a delete case, it only handles adding and updating notes. If you simply remove a note from your markdown notes, it will not be contained in the resulting Anki package. But importing that package will not remove the existing Anki note. That one will live on.

That being said, there is a suggested process for deleting markdown notes and keeping your markdown notes and Anki notes in sync.

1. Create some kind of global delete markdown notes file that gets tagged with e.g.  `global_delete`.
2. Whenever you want to remove a markdown note, move it into that file instead.
3. Now run `manki` and update Anki.
4. Now use the Anki browser to search for `tag:global_delete`.
5. Delete the notes in Anki, then also delete the notes in the global delete markdown notes file.
6. The note is now deleted and markdown and Anki are still in sync.

### Tags

### Media Files

You must use media files with globally unique filenames (not filepaths but actual filenames). For any duplicate filenames, only the initial one will end up in the Anki package. Anki uses a single media directory per collection. Anki cards implicitly source (e.g. within `img` tags) from that directory.
