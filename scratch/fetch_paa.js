const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJfU1ozX0hqOXpTSnUzb19vX1ZmX0RRemNhZWxzb254NklhQS03QUs4aUhMeWFVaW1yX2EzUmw5cTBRSm5LbmVtYTh1c0FNTnZ4YXI3VlhLOSIsImlhdCI6MTc3Njc4OTYzMn0.NVUqTbkdV__bAW7OeN7xYHWMAzCLP82O7XMnPgvnQYA";
const API_URL = "https://dados.gov.br/dados/api/publico/conjuntos-dados";

async function runValidation() {
    console.log("Tentando conexão oficial com Token de Consumidor...");
    
    try {
        const response = await fetch(`${API_URL}?q=Programa de Aquisição de Alimentos`, {
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
                'Accept': 'application/json'
            }
        });

        if (response.status === 401) {
            console.error("ERRO: Token não aceito pelo servidor (401). Verifique se o token expirou.");
            return;
        }

        const data = await response.json();
        // Na nova API, os dados vêm em 'content'
        const datasets = data.content || [];
        
        console.log("\n--- CONJUNTOS DE DADOS LOCALIZADOS ---");
        console.table(datasets.map(d => ({
            ID: d.id,
            Titulo: d.titulo,
            Organizacao: d.organizacao ? d.organizacao.nome : "N/A"
        })));

    } catch (e) {
        console.error("Erro na comunicação:", e.message);
    }
}

runValidation();
