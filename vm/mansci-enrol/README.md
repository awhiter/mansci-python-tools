# ManSci module enrolment command

Single student:

```text
mansci-enrol MSIN0010 uczzzz1
```

List of students (one UCL username per line; blank lines and `#` comments are ignored):

```text
mansci-enrol MSIN0010 --file students.txt
```

The configured module lead may use the command only for their own module.
`mansci-build` may use it for any configured module. Missing accounts are created
after prompting invisibly for one initial password. Existing accounts, passwords,
files, and workspaces are preserved. Repeating an enrolment is safe.

The protected backend validates the caller, module, usernames, account type,
teaching source, links, and destination objects before recording enrolment in
`/etc/mansci/enrolments/<module>_students.txt`.

## Reviewing current enrolments

List enrolled usernames or return only their count:

```text
mansci-enrol MSIN0010 --list
mansci-enrol MSIN0010 --count
```

These read-only operations apply the same module-lead authorisation check as enrolment.

## Removing an enrolment

```text
mansci-unenrol MSIN0010 uczzzz1
mansci-unenrol MSIN0010 --file students.txt
```

Unenrolment removes the module link from Teaching Materials and removes the
username from the module enrolment list. It deliberately preserves the Unix
account and everything under My Work. Repeating the operation is safe.
