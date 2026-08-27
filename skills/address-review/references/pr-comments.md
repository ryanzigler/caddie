# Reading and answering PR review comments with `gh`

Every command on one line. `{owner}/{repo}` is filled in by `gh` from the current remote.
`N` is the PR number.

## Read

Top-level review bodies (verdicts and summaries from `claude[bot]`, `macroscopeapp[bot]`,
humans):

```
gh api "repos/{owner}/{repo}/pulls/N/reviews" --paginate -q '.[] | select(.body != "") | {id, user: .user.login, state, commit: .commit_id, body}'
```

Unresolved inline threads, with the comments in each. This is the only endpoint that
exposes `isResolved`, so use it rather than the REST comments list:

```
gh api graphql -F owner='{owner}' -F repo='{repo}' -F pr=N -f query='query($owner:String!,$repo:String!,$pr:Int!){ repository(owner:$owner,name:$repo){ pullRequest(number:$pr){ reviewThreads(first:100){ nodes{ id isResolved isOutdated path line originalLine comments(first:20){ nodes{ databaseId author{login} body createdAt } } } } } } }' -q '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved|not)'
```

`isOutdated: true` means the branch moved past the commented line; re-locate the code before
judging the claim. `id` here is the GraphQL thread id used to resolve; `databaseId` on the
first comment is the REST id used to reply.

Issue-level comments (review bots that post one summary comment, and humans):

```
gh api "repos/{owner}/{repo}/issues/N/comments" --paginate -q '.[] | select(.user.login | test("vercel|github-actions|dependabot|codecov|changeset") | not) | {id, user: .user.login, body}'
```

## Reply

Reply inside an inline thread (REST id of the thread's first comment):

```
gh api -X POST "repos/{owner}/{repo}/pulls/N/comments/COMMENT_ID/replies" -f body='Fixed in abc1234: <what changed>.'
```

Reply to a top-level review or issue comment:

```
gh pr comment N --body '<reply>'
```

Resolve a thread you fixed (GraphQL thread id):

```
gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -F id='THREAD_ID'
```

Resolve only threads whose fix is committed and pushed. Leave refuted and out-of-scope
threads open so the reviewer sees the reasoning and can close them.
