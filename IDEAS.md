# Ideas to consider

## All components
 * Fix dependency management
 * Statsd
 * Central logging a la logstash
 * It is exists, it should have at least one munin graph
 * Re-layout codebase

## Editor
 * Replace the editor with ACE
 * Fix connection to multiplexer to use websockets
 * Proper code settings that are public/private and delivered as env-vars to sandbox
 * User themes
 * Localstorage based code-backup
 
## Site
 * Upgrade Django
 * Improve user 'dashboard'
 * Proper search
 * Move database to Postgres
 * Fix permissions to use built-in perms
 * Replace 'views' with a tickbox that allows running out of scheduler (only) and outputs back via wsgi.
 * Improve code management to make it easier to re-use 
 
## Code management
 * Allow code-signing
 * Revision code in local git repo instead of hg
 * Make sure git is per-user
 * Expose git API to end-users
 * Allow dependency queues for code (x should run after y after z)

## Multiplexer
 * Remove scheduling to separate DB-backed process
 * Act as proxy for skypipe
 * Support more than one sandbox
 * Integrate OTransform

## Scheduling
 * Look at using redis.
 * Look at using AQMP topic queues.
 * Handle backlog
 * Notify users on backlog
 * Notify admins on backlog
 * Allow a re-layout of times to cover fully 24h
 * Notify affected users of re-layout.

## Code sandbox
 * docker.io
 * Allow code-signing
 * Use skypipe style app to send output (might allow debugging)
 * Provide localised logging that can be viewed in editor
 * Remove httpproxy.
 * Allow customisation of images from a manifest outside the container
 * ScriptMgr to do nothing except launch container, container should be responsible for talking to multiplexer.
 * Consider making sandbox get the code from git instead of delivering it to the sandbox directly

## API
 * Expose scheduling via API

## Data storage
 * Fix. Replace. Burn it with fire.
 * Make sure the 'scraperlibs' protocol is replaced with something usable from other languages easily.

## Remove
 * Vaults (replace with collections)
 * Unused components/dependencies
 
 