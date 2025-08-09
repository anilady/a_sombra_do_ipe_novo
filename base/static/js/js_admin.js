function pesquisarColaborador() {
  let input = document.getElementById('pesquisa').value.toLowerCase();
  let rows = document.querySelectorAll('#tabela-colaboradores tr');
  
  rows.forEach(row => {
    const texto = row.innerText.toLowerCase();
    row.style.display = texto.includes(input) ? '' : 'none';
  });
}

function limparPesquisa() {
  document.getElementById('pesquisa').value = '';
  pesquisarColaborador(); // Reseta a busca
}

function ordenarTabela() {
  // Exemplo simples de ordenação alfabética
  let tabela = document.getElementById('tabela-colaboradores');
  let linhas = Array.from(tabela.rows);
  linhas.sort((a, b) => a.cells[0].innerText.localeCompare(b.cells[0].innerText));
  linhas.forEach(linha => tabela.appendChild(linha));
}

function exportarCSV() {
  let csv = "COLABORADOR,EMAIL,STATUS\n";
  let rows = document.querySelectorAll("#tabela-colaboradores tr");
  rows.forEach(row => {
    let cols = row.querySelectorAll("td");
    if (cols.length > 0) {
      csv += `${cols[0].innerText},${cols[1].innerText},${cols[2].innerText}\n`;
    }
  });
  let blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  let link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "colaboradores.csv";
  link.click();
}

function gerarGrafico() {
  // Chame uma lib como Chart.js aqui
  alert("Função de gráfico ainda não implementada.");
}
