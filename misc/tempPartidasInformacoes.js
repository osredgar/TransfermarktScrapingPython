const penaltyShootOut = "https://www.transfermarkt.com.br/spielbericht/index/spielbericht/4111940"
const missedPenalty = "https://www.transfermarkt.com.br/spielbericht/index/spielbericht/4061234"
const ownGoal = "https://www.transfermarkt.com/spielbericht/index/spielbericht/4810955"
const secondYellow = "https://www.transfermarkt.com/spielbericht/index/spielbericht/987570"

details = []
matches = []

function getMatchTeams(document) {
	div = document.querySelectorAll("div.sb-team:not(.hide-for-small) a.sb-vereinslink")

	div.forEach((el) => {
		if (el.parentNode.classList.contains("sb-heim")) {
			homeTeamID = el.getAttribute("href").split("/verein/").at(-1).split("/").at(0)
			homeTeam = el.getAttribute("title").trim()
			return
		}

		if (el.parentNode.classList.contains("sb-gast")) {
			awayTeamID = el.getAttribute("href").split("/verein/").at(-1).split("/").at(0)
			awayTeam = el.getAttribute("title").trim()
			return
		}
	})

	details.concat({ homeTeamID, homeTeam, awayTeamID, awayTeam })
}

function getMatchInfos(document) {
	div = document.querySelector("div.sb-spieldaten")

	children = div.querySelector("p.sb-datum").innerText.split("|")
	matchday = children.at(0).trim()
	time = children.at(2).trim()

	children = div.querySelector("a")
	date = children.getAttribute("href").split("/datum/").at(-1)

	children = div.querySelectorAll("p.sb-zusatzinfos a")

	div.forEach((el) => {
		link = el.getAttribute("href")

		if (link.match("verein") !== null) {
			stadiumID = link.split("/verein/").at(-1).split("/").at(0)
			stadium = el.childNodes[0].textContent.trim()
			return
		}

		if (link.match("schiedsrichter") !== null) {
			refereeID = link.split("/schiedsrichter/").at(-1).split("/").at(0)
			referee = el.childNodes[0].textContent.trim()
			return
		}
	})

	details.concat({ stadiumID, stadium, refereeID, referee })
}

function getMatchGoals(document) {
	homeGoals = document.querySelectorAll("div#sb-tore li.sb-aktion-heim").length * 1
	awayGoals = document.querySelectorAll("div#sb-tore li.sb-aktion-gast").length * 1

	homePenScored = null
	homePenMissed = null
	awayPenScored = null
	awayPenMissed = null

	hasPenaltyShootOut = document.querySelectorAll("div#sb-elfmeterscheissen").length !== 0

	if (hasPenaltyShootOut === true) {
		homePenMissed = document.querySelectorAll("div#sb-elfmeterscheissen li.sb-aktion-heim div.sb-aktion-uhr span.sb-11m-verschossen").length * 1
		homePenScored = document.querySelectorAll("div#sb-elfmeterscheissen li.sb-aktion-heim div.sb-aktion-uhr span.sb-11m-tor").length * 1
		awayPenScored = document.querySelectorAll("div#sb-elfmeterscheissen li.sb-aktion-gast div.sb-aktion-uhr span.sb-11m-tor").length * 1
		awayPenMissed = document.querySelectorAll("div#sb-elfmeterscheissen li.sb-aktion-gast div.sb-aktion-uhr span.sb-11m-verschossen").length * 1
	}

	return JSON.stringify({ homeGoals, homePenScored, homePenMissed, awayGoals, awayPenScored, awayPenMissed, hasPenaltyShootOut }, null, 2)

	// details.concat({ homeGoals, homePenScored, homePenMissed, awayGoals, awayPenScored, awayPenMissed })
}

function getMatchGoalsDetails(document, homeTeamID, awayTeamID) {
	events = []

	rows = document.querySelectorAll("div#sb-tore div.sb-aktion")

	rows.forEach((row) => {
		parentClass = row.parentNode.classList

		teamID = 0
		playerID = 0
		player = null
		minute = null
		minuteAdc = null
		info = null
		kind = null

		action = row.querySelector("div.sb-aktion-uhr span")

		minute = action.style.backgroundPosition
		minuteAdc = action.innerText.trim()

		teamID = row.querySelector("div.sb-aktion-wappen a").getAttribute("href").split("/verein/").at(-1).split("/").at(0) * 1

		actions = row.querySelectorAll("div.sb-aktion-aktion a")
		actions.forEach((action) => {
			playerID = action.getAttribute("href").split("/spieler/").at(-1).split("/").at(0) * 1
			player = action.innerText.trim()

			infoText = action.nextSibling.textContent
			info = infoText.split(", ", 2).at(-1)

			if (infoText.match("Goal") !== null) {
				kind = "Goal"
			} else {
				kind = "Assist"
			}

			if (info.match("Tournament") !== null) {
				info = null
			}

			switch (true) {
				case info === "Own-goal" && teamID === homeTeamID:
					teamID = awayTeamID
					break

				case info === "Own-goal" && teamID === awayTeamID:
					teamID = homeTeamID
					break

				default:
					break
			}

			events.push({ teamID, playerID, player, kind, info, minute, minuteAdc })
		})
	})

	return JSON.stringify(events, null, 2)
}

function getMatchCards() {
	events = []

	rows = document.querySelectorAll("div#sb-karten div.sb-aktion")

	rows.forEach((row) => {
		parentClass = row.parentNode.classList

		teamID = 0
		playerID = 0
		player = null
		minute = null
		minuteAdc = null
		info = null
		kind = null

		action = row.querySelector("div.sb-aktion-uhr span")

		minute = action.style.backgroundPosition
		minuteAdc = action.innerText.trim()

		teamID = row.querySelector("div.sb-aktion-wappen a").getAttribute("href").split("/verein/").at(-1).split("/").at(0) * 1

		action = row.querySelector("div.sb-aktion-spielstand span")
		switch (true) {
			case action.classList.contains("sb-rot"):
				kind = "Red card"
				break

			case action.classList.contains("sb-gelbrot"):
				kind = "2nd Yellow card"
				break

			default:
				kind = "Yellow card"
				break
		}

		actions = row.querySelectorAll("div.sb-aktion-aktion a")
		actions.forEach((action) => {
			playerID = action.getAttribute("href").split("/spieler/").at(-1).split("/").at(0) * 1
			player = action.innerText.trim()

			info = null
			infoText = action.parentNode.textContent
			if (infoText.match(",") !== null) {
				info = infoText.split(", ", 2).at(-1)
			}

			events.push({ teamID, playerID, player, kind, info, minute, minuteAdc })
		})
	})

	return JSON.stringify(events, null, 2)
}

matches.push(details)
console.log(JSON.stringify(matches, null, 2))
