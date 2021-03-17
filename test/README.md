# Testing on the browser

`npm run selenium` will launch all unit tests cointained in 
`test/browserstack/scripts/automate`.

The `gauge-displays` directory contains code created for determining layout
breakpoints across display devices and configurations. Though this code is not 
well organized nor easy to read, it's serving as the basis for running more 
tests directly in the browser through Browserstack using Selenium.

However, it still needs some heavy refactoring and cleanup.

A Github action is configured in `.github/workflows/node.js.yml` to 
automatically launch the Selenium tests on Browserstack when pushing to a PR.
Forks of the repository should be configured with the following secrets in the
settings in Github:

 * `BROWSERSTACK_USERNAME`: The account name to use in Browserstack.
 * `BROWSERSTACK_KEY`: The access key provided by Browserstack.
 * `BROWSERSTACK_GIST_TOKEN`: A Github token authorized to create Gists.

TODO:

 * Rewrite test runner in functional style, separating test-list generation from 
   test running.
 * Add Browserstack session & queue management.
 * Describe testing setup procedure on Browserstack and Github.
 * Run on all os/browser/version configurations available on Browserstack.
