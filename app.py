import os
import re
import random
import unicodedata
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# ----------------------------------------------------------------------------
# App setup
# ----------------------------------------------------------------------------
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)




# ----------------------------------------------------------------------------
# Utils
# ----------------------------------------------------------------------------
def remover_acentos(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn')

# ----------------------------------------------------------------------------
# Categorias (mesmo formato do código original)
# Cada categoria tem "padroes" (palavras-chave/regex) e "respostas".
# ----------------------------------------------------------------------------
categorias = {
    # Saudações e conversa básica
    "saudacao": {
        "padroes": [
            r"\b(oi|ol[aá]|e[ií]|e a[ií]|bom dia|boa tarde|boa noite)\b"
        ],
        "respostas": [
            "Olá! Sou a assistente do Senac Serra. Como posso te ajudar hoje?",
            "Oi! Bem-vindo(a) ao Senac Serra. O que você gostaria de saber?",
            "Olá! Posso tirar dúvidas sobre cursos, inscrições, valores e muito mais."
        ]
    },

    "despedida": {
        "padroes": [r"\b(tchau|ate logo|ate mais|obrigado,? por enquanto|valeu,? ate|ate breve)\b"],
        "respostas": [
            "Até mais! Se precisar, é só chamar.",
            "Tchau! Estarei por aqui quando precisar.",
            "Até logo! Conte com o Senac Serra."
        ]
    },

    # Informações institucionais do Senac Serra
    "o_que_e_senac": {
        "padroes": [
            r"\b(o que (e|é) (o )?senac|sobre o senac|quem (sao|são) voces|quem (e|é) voces)\b"
        ],
        "respostas": [
            "O Senac é uma instituição de educação profissional. No Senac Serra oferecemos cursos livres, técnicos e programas de qualificação em diversas áreas para você se preparar para o mercado de trabalho.",
        ]
    },

    "localizacao": {
        "padroes": [
            r"\b(on(de|de fica)|endereco|endereço|localiza(ca|ç)ao|mapa)\b"
        ],
        "respostas": [
            "Estamos no Senac Serra (ES). Endereço: Av. Talma Rodrigues Ribeiro, 2881 - Portal de Jacaraípe, Serra - ES, 29173-795. Se precisar, te envio instruções de como chegar de ônibus.",
        ]
    },

    "telefone_contato": {
        "padroes": [
            r"\b(telefone|contato|falar com atendente|numero|n[uú]mero|whats|whatsapp)\b"
        ],
        "respostas": [
            "Você pode entrar em contato com nossa equipe pelo telefone/WhatsApp da unidade por esse número: Telefone: (27) 3243-8153.",
        ]
    },

    "horario_funcionamento": {
        "padroes": [
            r"\b(hor[aá]rio(s)?|funciona que horas|abre que horas|fecha que horas|qual (o )?horario)\b"
        ],
        "respostas": [
            "O Senac Serra funciona dás 8:00 até as 22:00, mas os horários de atendimento podem variar conforme o período de matrículas e agenda de cursos. Recomendo confirmar no telefone/WhatsApp da unidade para o dia que você pretende ir.",
        ]
    },

    # Cursos e inscrições
    "cursos_disponiveis": {
        "padroes": [
            r"\b(curso(s)? dispon[ií]vel(is)?|quais cursos tem?|lista de cursos|oferta de cursos|quais são os cursos que oeferece?)\b"
        ],
        "respostas": [
            "Oferecemos cursos em áreas como Administração, Tecnologia, Gastronomia, Beleza, Saúde e mais. Se me disser a área de interesse, eu te direciono melhor.",
        ]
    },

    "inscricoes_matricula": {
        "padroes": [
            r"\b(inscri(c|ç)[aã]o|matr[ií]cula|como me inscrevo|quero me matricular)\b"
        ],
        "respostas": [
            "Para se inscrever, você pode ir à unidade com documento oficial e, quando necessário, comprovante de escolaridade. Em alguns cursos é possível realizar a inscrição on-line.",
        ]
    },

    "valores_pagamento": {
        "padroes": [
            r"\b(valor(es)?|pre(c|ç)o(s)?|mensalidade(s)?|quanto custa|formas de pagamento|paga como|parcelamento)\b"
        ],
        "respostas": [
            "Os valores variam conforme o curso e a carga horária. O pagamento geralmente pode ser à vista ou parcelado. Se quiser, você pode saber mais entrando no site oficial do Senac Serra (ES).",
        ]
    },

    "gratuidade_psg": {
        "padroes": [
            r"\b(gratuidade|psg|bolsa|curso gratuito|bolsas)\b"
        ],
        "respostas": [
            "O Senac possui o Programa Senac de Gratuidade (PSG), com vagas em cursos gratuitos para quem atende aos critérios do programa. As vagas são limitadas e divulgadas periodicamente.",
        ]
    },

    "modalidades_ead_presencial": {
        "padroes": [
            r"\b(ead|a distancia|on-line|online|presencial|h[ií]brido|hibrido|modalidade)\b"
        ],
        "respostas": [
            "O Senac Serra oferece cursos nas duas modalidades: presencial (nas instalações da unidade) e EAD (a distância, por meio do Senac EAD Nacional, com o polo da Serra como apoio).",
        ]
    },
    "tecnologia": {
        "padroes": [
            r"\b(Tecnologia|tecnologia|informatica|informática|sistemas|computacao|computação|computador|computadores|internet|inteligencia artificial)\b"
        ],
        "respostas": [
            "Existem diversos cursos disponíveis na unidade Serra na área de tecnologia: Técnico em informática, Técnico em desenvolvimento de sistemas, Informática básica, Excel básico, Excel avançado, Power Bi, MS Project, Canva para educação e para empresas, Jovem programadora e entre outros.",
        ]

    },
    "professores": {
        "padroes": [
            r"\b(professores|como sao os professores?|tem bons professores?|tem professores capacitados?)\b"
        ],
        "respostas": [
            "Os professores do Senac Serra têm experiência prática no mercado, atuam como mediadores da aprendizagem, utilizam metodologias ativas, estimulam o ciclo ação-reflexão-ação, acompanham de perto o desenvolvimento dos estudantes e passam por formação continuada para se manterem atualizados e alinhados ao Modelo Pedagógico do Senac.",
        ]

        
    },

    # Estrutura e serviços
    "infraestrutura": {
        "padroes": [
            r"\b(estrutura|infraestrutura|laborat[oó]rio(s)?|cozinha pedag[oó]gica|salas|equipamentos|biblioteca|banheiros)\b"
        ],
        "respostas": [
            "De forma geral, a infraestrutura conta com: Salas de aula modernas com recursos multimídia e ambiente confortável. Laboratórios de informática equipados com tecnologia atualizada para atividades digitais. Cozinha pedagógica para cursos da área de gastronomia, com equipamentos profissionais. Salão de beleza e estética para práticas em beleza, cabelo, maquiagem e estética. Laboratórios de saúde ambientes que simulam clínicas e consultórios para cursos técnicos em saúde. Biblioteca com acervo físico e digital de apoio ao estudo. Ambientes de atendimento ao público em alguns cursos, os alunos vivenciam situações reais de trabalho com clientes. Espaços multiuso que podem ser adaptados para diferentes situações de aprendizagem e projetos integradores. Essa estrutura é pensada para que os alunos aprendam fazendo, com metodologias ativas, vivências reais e contato direto com situações práticas.",
        ]
    },

    "estagio_empregabilidade": {
        "padroes": [
            r"\b(est[aá]gio|emprego|empregabilidade|parceria com empresas|oportunidade(s) de trabalho)\b"
        ],
        "respostas": [
            "O Senac mantém relacionamento com empresas parceiras e divulga oportunidades para alunos conforme as áreas. Alguns cursos incluem atividades práticas e encaminhamentos.",
        ]
    },

    "documentos_requisitos": {
        "padroes": [
            r"\b(documento(s)?|requisito(s)?|idade m[ií]nima|escolaridade|pr[eé]-requisito(s)?)\b"
        ],
        "respostas": [
            "Os requisitos variam por curso (idade mínima e escolaridade). Se quiser, eu te passo os requisitos gerais.",
        ]

    },

    "requisitos_gerais": {
        "padroes": [
            r"\b(quero saber mais|quais os requisitos?|quais sao os requisitos?|eu quero|me fale os requisitos)\b"
        ],
        "respostas": [
            "Os requisitos de documentos podem variar conforme o curso escolhido (livre, técnico, graduação ou pós). Mas, em geral, o Senac Serra solicita os seguintes documentos no ato da matrícula:  Documento de identidade oficial com foto (RG, CNH ou equivalente)CPFComprovante de residência atualizadoComprovante de escolaridade compatível com o cursoPara menores de 18 anos:  documentos do responsável legal No caso de cursos técnicos ou de nível superior, pode ser necessário apresentar histórico escolar ou certificado de conclusão da etapa anterior (ensino fundamental ou médio, conforme o caso).",
        ]
    },

    "linha de onibus": {
    "padroes": [
        r"\b(linha(s)?|onibus|transcol|busao)\b"
    ],
    "respostas": [
        "Uma das linhas de ônibus que passam em frente ao Senac Serra é o 805B que é a linha que o caminho é para o bairro Feu Rosa,504,523 e 875",
        
    ]

    },

    "requisitos para incriçao": {
    "padroes": [
        r"\b(sim|quero saber mais|como me inscrever?|como se increver?|como entrar no senac?)\b"
    ],
    "respostas": [
        "Os requisitos para inscrição em um curso no Senac Serra (ES) podem variar de acordo com o tipo de curso escolhido (livres, técnicos, de graduação ou pós-graduação). Em geral, são pedidos:"
        "Documentos pessoais: RG, CPF e comprovante de residência atualizado. Comprovante de escolaridade: varia conforme o curso (por exemplo, estar cursando ou ter concluído o ensino médio para cursos técnicos"
        "Idade mínima: cada curso pode exigir uma idade mínima (alguns a partir de 14, outros 16 ou 18 anos). Pagamento da matrícula (quando não for bolsa ou gratuidade).",
        
    ]

    },

    "gastronomia": {
    "padroes": [
        r"\b(gastronomia|cozinha|curso de gastronomia)\b"
    ],
    "respostas": [
        "O curso de Gastronomia no Senac é bastante reconhecido pela qualidade de ensino e pela infraestrutura que possibilita ao estudante aprender na prática. Ele pode ser encontrado em diferentes formatos: cursos livres (curta duração), cursos técnicos e curso superior de tecnologia em Gastronomia. Curso Superior de Tecnologia em GastronomiaDuração aproximada: 2 anos.Objetivo: formar profissionais capacitados para atuar na produção, gestão e criação na área gastronômica. Conteúdos principais:Técnicas de cozinha nacional e internacionalPanificação e confeitariaNutrição aplicada à gastronomiaGestão de alimentos e bebidasHigiene e segurança alimentarEmpreendedorismo e gestão de negócios gastronômicosSustentabilidade e inovação na gastronomiaCursos Técnicos e Livres em GastronomiaCursos técnicos: voltados para atuação prática e inserção rápida no mercado de trabalho. Cursos livres: de curta duração, com foco em áreas específicas, como: confeitaria, panificação, cozinha básica, cozinha japonesa, cozinha italiana, dentre outros. São ideais para quem deseja desenvolver habilidades específicas ou se especializar em determinado segmento. Infraestrutura para apoio às aulasCozinhas pedagógicas equipadas com fogões industriais, bancadas, utensílios e câmaras frias.Laboratórios de panificação e confeitaria. Espaços que simulam ambientes de restaurantes, possibilitando práticas de atendimento.",
    ]

    },

    "lanches": {
    "padroes": [
        r"\b(lanche|cozinha|comida|cantina|lanchonete|comprar)\b"
    ],
    "respostas": [
        "No Senac Serra, assim como em outras unidades do Senac, normalmente há cantina/lanchonete ou espaço de convivência onde os estudantes podem comprar lanches nos intervalos das aulas. Esse serviço pode variar conforme o turno e a demanda de alunos. Em algumas situações, quando não há lanchonete interna funcionando, os estudantes utilizam os comércios próximos à unidade.",
    ]


    },

    "administraçao": {
    "padroes": [
        r"\b(administraçao|curso de administraçao|administrar)\b"
    ],
    "respostas": [
        "O curso Técnico em Administração do Senac tem como objetivo preparar o estudante para atuar em diferentes áreas administrativas, como gestão de pessoas, logística, marketing, finanças e processos organizacionais. Ele é estruturado com base no Modelo Pedagógico do Senac (MPS), que valoriza o protagonismo do estudante e a aprendizagem baseada em competências, aproximando teoria e prática.De forma geral, o curso contempla:Gestão de processos organizacionaisRotinas de departamento pessoal e recursos humanosNoções de contabilidade e finanças. Planejamento estratégico e marketingProjetos e inovação profissional formado pode atuar em empresas de diferentes portes e setores, órgãos públicos ou iniciar seu próprio negócio.",
    ]

    },

    "moda": {
    "padroes": [
        r"\b(moda|estilo|modelo)\b"
    ],
    "respostas": [
        "O Senac oferece formações em Moda que podem variar de cursos livres a cursos técnicos e superiores, dependendo da unidade. No caso do Senac Serra, o foco principal é preparar o estudante para atuar no mercado de moda de forma criativa e empreendedora, sempre com base no Modelo Pedagógico do Senac. De forma resumida, os cursos de Moda trabalham: Criação e desenvolvimento de coleções: do conceito ao produto final.  Desenho e modelagem: técnicas manuais e digitais.  Costura e acabamento: prática para confecção de peças.  Gestão e marketing de moda: visão de negócios, branding e tendências.  Sustentabilidade: incentivo a práticas conscientes na cadeia da moda.  O estudante desenvolve competências para atuar como estilista, modelista, produtor de moda, consultor de estilo ou gestor em empresas e marcas do setor, além de poder empreender o próprio negócio.",
    ]
 },

    "inauguraçao": {
    "padroes": [
        r"\b(quando foi inaugurado|quantos anos tem o senac serra?|fundacao|inaugurado|inauguraçao|fundado)\b"
    ],
    "respostas": [
        "O Senac Serra, localizado no Espírito Santo, foi inaugurado em 2021. A unidade é uma das mais novas do Senac-ES e foi criada para atender à forte demanda de formação profissional na região, que se destaca pelo crescimento industrial, comercial e de serviços. Desde sua inauguração, o Senac Serra oferece cursos em diversas áreas, como gestão, tecnologia, saúde, gastronomia, moda e beleza, sempre com base no Modelo Pedagógico do Senac (MPS), que valoriza a prática, a aprendizagem por competências e o protagonismo do estudante.",
    ]
    

    },

    # Fallback
    "padrao": {
        "padroes": [],
        "respostas": [
            "Posso te ajudar com informações sobre cursos, inscrições, valores, modalidades e estrutura do Senac Serra. Pode me dizer o que você precisa?",
            "Não tenho certeza se entendi. Você quer saber sobre cursos, valores, inscrições, horários ou localização?",
            "Certo. Me diga a área de interesse (por exemplo, Administração, Tecnologia ou Gastronomia) e eu te oriento."
        ]
    },
}

# ----------------------------------------------------------------------------
# Detecção de categoria (mesma lógica geral do original)
# ----------------------------------------------------------------------------
def detectar_categoria(mensagem: str):
    mensagem_norm = remover_acentos(mensagem.lower())

    melhor_cat = "padrao"
    melhor_score = 0

    for cat, info in categorias.items():
        if cat == "padrao":
            continue
        score = 0
        for padrao in info["padroes"]:
            if re.search(padrao, mensagem_norm, re.IGNORECASE):
                palavras = re.findall(r"\b([a-z0-9]+)\b", padrao)
                for p in palavras:
                    if p in mensagem_norm:
                        score += 1
        if score > melhor_score:
            melhor_score = score
            melhor_cat = cat

    resposta = random.choice(categorias[melhor_cat]["respostas"])
    return melhor_cat, resposta

# ----------------------------------------------------------------------------
# Rotas
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json(silent=True) or {}
    mensagem = dados.get("mensagem", "").strip()
    if not mensagem:
        return jsonify({"categoria": "erro", "resposta": "Mensagem vazia."}), 400
    categoria, resposta = detectar_categoria(mensagem)
    return jsonify({"categoria": categoria, "resposta": resposta})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
