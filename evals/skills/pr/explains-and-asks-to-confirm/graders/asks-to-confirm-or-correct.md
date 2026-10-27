---
type: regex
pattern: '(?:^|\n[ \t]*\n)(?=(?:(?!\n[ \t]*\n)[\s\S])*?\bconfirm(?!ed))(?=(?:(?!\n[ \t]*\n)[\s\S])*?\bcorrect(?!ion|ed))(?=(?:(?!\n[ \t]*\n)[\s\S])*?\?)'
flags: i
---
One question asks the author to confirm or correct: "confirm" and "correct" come in the same paragraph as a question mark, in any order; "confirmed", "correction" and "corrected" do not count.
