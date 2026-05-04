partidas = []

rodadas = document.querySelectorAll("div.row:nth-child(5) div.large-6 tbody tr")

rodadas.forEach((rodada) => {
	nomeRodada = rodada.parentNode.parentNode.parentNode.firstElementChild.textContent.trim()

	if (rodada.classList.length === 1) {
		if (rodada.getAttribute("class") === "bg_blau_20") {
			el = rodada.querySelector("td.show-for-small")
			hora = el.firstChild.textContent.trim()

			if (el.firstElementChild !== null) {
				data = el.firstElementChild.getAttribute("href").split("/datum/").at(-1)
				hora = el.firstElementChild.nextSibling.textContent.trim()
			}
			return
		}
	}

	el = rodada.querySelector("td.text-right.no-border-rechts.hauptlink a")
	mandanteID = 0
	mandante = "TBD"

	if (el !== null) {
		mandanteID = el.getAttribute("href").split("/verein/").at(-1).split("/").at(0) * 1
		mandante = el.childNodes[0].textContent.trim()
	}

	el = rodada.querySelector("td.no-border-links.hauptlink a")
	visitanteID = 0
	visitante = "TBD"

	if (el !== null) {
		visitanteID = el.getAttribute("href").split("/verein/").at(-1).split("/").at(0) * 1
		visitante = el.childNodes[0].textContent.trim()
	}

	el = rodada.querySelector("td.zentriert.hauptlink a")
	partidaID = 0
	jogoRealizado = false
	partida = "TBD"

	if (el !== null) {
		partidaID = el.getAttribute("href").split("/spielbericht/").at(-1) * 1
		jogoRealizado = el.hasAttribute("id")
		partida = `${mandante} x ${visitante}`
	}

	placar = null
	golMandante = null
	golVisitante = null

	if (jogoRealizado === true) {
		placar = el.childNodes[0].textContent.trim()
		golMandante = placar.split(":").at(0) * 1
		golVisitante = placar.split(":").at(-1) * 1
	}

	partidas.push({
		partidaID,
		partida,
		nomeRodada,
		data,
		hora,
		mandanteID,
		mandante,
		visitanteID,
		visitante,
		placar,
		golMandante,
		golVisitante,
		jogoRealizado,
	})
})

console.log(JSON.stringify(partidas, null, 2))
