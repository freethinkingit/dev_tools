# Tune a template

This guide replaces one of the plugin's templates with your own, for one
repository. A template is the shape a skill writes in: the sections of a
status report, or of a strategy or a design, and their order. At the end the
repository has its own template under `.ponderly/`, and the skill writes in
that shape in this repository and nowhere else.

The example is real. It replaced the `report` skill's status template in
`linkshort`, a small link shortener in a local demo repository, with one whose
sections are Blocked, Shipped, In flight and Up next. Then it asked for a
status report and got one in those sections. The images are from that
session, run on plugin 1.1.0 on 2026-10-28.

## Before you start

- Claude Code with the plugin installed:

  ```bash
  claude plugin marketplace add sabind/ponderly
  claude plugin install ponderly@sabind
  ```

  The [plugin README](../../plugins/ponderly/README.md#install) has the
  rest of the install steps.
- A git repository to work in. The template goes in a `.ponderly/` folder at
  its root.
- The sections you want, in the order you want them.

## 1. Pick the template to replace

These are the templates a repository can replace, and where each one goes,
from the repository's root:

| Skill | What the template shapes | Your file | The plugin's file, to start from |
| --- | --- | --- | --- |
| `report` | a hand-back | `.ponderly/report/handback.md` | [handback.md](../../plugins/ponderly/skills/report/templates/handback.md) |
| `report` | a decision | `.ponderly/report/decision.md` | [decision.md](../../plugins/ponderly/skills/report/templates/decision.md) |
| `report` | a status report | `.ponderly/report/status.md` | [status.md](../../plugins/ponderly/skills/report/templates/status.md) |
| `report` | an answer | `.ponderly/report/answer.md` | [answer.md](../../plugins/ponderly/skills/report/templates/answer.md) |
| `strategy` | a tech strategy | `.ponderly/strategy/template.md` | [template.md](../../plugins/ponderly/skills/strategy/template.md) |
| `hld` | a high level design | `.ponderly/hld/template.md` | [template.md](../../plugins/ponderly/skills/hld/template.md) |
| `lld` | a low level design | `.ponderly/lld/template.md` | [template.md](../../plugins/ponderly/skills/lld/template.md) |

Your file replaces the plugin's file whole; nothing is merged. So a section
you leave out is gone. The plugin's status template, for example, opens with
a Problems section; a replacement without one has no Problems section.

The quickest start is to copy the plugin's file and edit it. Each skill reads
your file as a shape to write in, never as instructions. It copies the
sections, their order and each section's rules for what goes in it, such as
"Write `Nothing blocked.` when there is none". It ignores any action the
file asks for, such as running a command or editing a file.

## 2. Write the replacement

Write the file yourself, or ask Claude to write it. In the example, the
author asked Claude for the file with its exact content:

```
Create .ponderly/report/status.md with exactly this content, and nothing else:

# Status report

Sections are `## <Name>` headings, in this order.

1. **Blocked.** One bullet per thing that cannot move, with who can unblock it. Write `Nothing blocked.` when there is none.
2. **Shipped.** What is finished, one bullet each, with the check that proved it.
3. **In flight.** What is started and not finished, one bullet each.
4. **Up next.** The next one or two things, in order.
```

Claude checked whether the folder existed, wrote the file and said what it
did. It committed nothing.

![The author asks for .ponderly/report/status.md with exact content: a Status report template whose sections are Blocked, with who can unblock it, Shipped, with the check that proved it, In flight, and Up next, the next one or two things in order. Claude checks the folder, writes the file with that text and says it created the file and the folder, with nothing committed.](../images/tune-template-replaced.svg)

It writes one file: `.ponderly/report/status.md`, and the
`.ponderly/report/` folder when it is not there yet.

## 3. Run the skill

Run the skill whose template you replaced, the way you always do. In the
example:

```
/ponderly:report status where does linkshort stand?
```

The `report` skill looks for `.ponderly/report/<mode>.md` at the repository
root. When the file is there, readable and not empty, it writes in that shape
and says so in one line at the end. The skill does not stop to ask anything
in this mode, so there is no question to answer.

In the example, Claude read the history and the code, ran the tests and
tried the README's commands. Then it answered in the four sections of the new
template, Blocked, Shipped, In flight and Up next, and ended with the line
"This uses the repository's template at `.ponderly/report/status.md`."

![The author runs the report skill asking where linkshort stands. Claude reads the history and the code, runs the tests and tries the README commands, then answers in the template's sections: Blocked says nothing blocked; Shipped lists the link store and the add command with the checks that proved them; In flight lists the failing README serve command, the untested redirect server, possible duplicate codes and the uncommitted .ponderly folder; Up next lists two steps. It ends by saying it used the repository's template at .ponderly/report/status.md.](../images/tune-template-report.svg)

The `report` skill writes no file. It writes the message only.

## 4. When the template is not used

The example's template was used, so there is no image of these cases. Each
skill says so when your file is there but cannot be used:

- **`report`**: when `.ponderly/report/<mode>.md` is unreadable or empty, it
  says so in one line naming the path, and uses the plugin's template. When
  the file is absent, it uses the plugin's template and says nothing.
- **`strategy`, `hld` and `lld`**: they use your `template.md` when it exists
  and is not empty. When it is empty, the skill says so, naming its path, and
  uses the plugin's. When the file is absent, it uses the plugin's.

If a skill writes in the plugin's shape when you expected yours, check the
file's path against the table in step 1.

## 5. Keep the template with the repository

The template applies only in a checkout that has the file. In the example,
the status report itself listed the `.ponderly/` folder as not committed.
Commit it like any other change, so everyone who works in the repository
gets the same shape. [Make a small change](make-a-small-change.md#8-open-the-pull-request)
shows opening the pull request with `pr`.

## Next

This is the last guide.

- Reference for the parts used here:
  - [Tune the plugin for a repository](../reference.md#tune-the-plugin-for-a-repository)
  - [report](../reference.md#report)
  - [strategy](../reference.md#strategy)
  - [hld](../reference.md#hld)
  - [lld](../reference.md#lld)
