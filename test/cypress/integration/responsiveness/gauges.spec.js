// / <reference types="cypress" />

context('Actions', () => {
	beforeEach(() => {
		cy.visit('http://localhost:3000/font-test');
	})

	it('Load the test page', () => {
		cy.get('#info')
		.invoke('text')
		.then(text => cy.log(text));
	})
})
