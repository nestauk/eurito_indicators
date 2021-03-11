# Testing on the browser

`npm run selenium` will launch all unit tests cointained in 
`test/browserstack/scripts/automate`.

The `gauge-displays` directory contains code created for determining layout
breakpoints across display devices and configurations. Though this code is not 
well organized nor easy to read, it's serving as the basis for running more 
tests directly in the browser through Browserstack using Selenium.

However, it still needs some heavy refactoring and cleanup.

TODO:

 * Rewrite test runner in functional style, separating test-list generation from 
   test running.
 * Add Browserstack session & queue management.
 * Describe testing setup procedure on Browserstack and Github.
 * Run on all os/browser/version configurations available on Browserstack.
