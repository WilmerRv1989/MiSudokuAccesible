# MiSudokuAccesible

Sudoku acessível para o leitor de telas NVDA, para todas as idades.

O MiSudokuAccesible permite que pessoas cegas ou com baixa visão joguem sudoku com cada célula do tabuleiro legível por voz e em braille, e aprendam a resolvê-lo com um curso guiado e com dicas que explicam cada jogada. Foi pensado também para crianças.

Funciona com o NVDA 2026.1 ou posterior. Não precisa de Internet e não envia nenhum dado: seu progresso fica guardado só no seu computador.

## Por onde começar

Tudo se abre pelo menu do NVDA (NVDA+N), Ferramentas, MiSudokuAccesible:

* Se você nunca jogou sudoku, comece por **Aprender a jogar**, desde a lição 1.
* Se você já sabe jogar, escolha **Novo sudoku** ou experimente o **Sudoku do dia**.
* Se você travar em um sudoku, pressione **P** para uma dica.

O submenu tem:

* **Novo sudoku...:** escolher tamanho, nível e ajudas, e começar.
* **Continuar o sudoku:** só aparece se você tiver um sem terminar.
* **Sudoku do dia:** um novo a cada dia.
* **Aprender a jogar...:** o curso guiado.
* **Minhas estatísticas...:** sudokus resolvidos, tempos, dias seguidos e progresso no curso.
* **Atalhos de teclado...:** a lista de todas as teclas.

## Como se joga

O tabuleiro tem 9 linhas e 9 colunas, divididas em 9 blocos de 3 por 3. É preciso preenchê-lo de modo que cada linha, cada coluna e cada bloco tenha os números de 1 a 9, sem repetir nenhum. Alguns números já vêm colocados desde o início: são fixos e não podem ser mudados.

As linhas vão de cima para baixo e as colunas da esquerda para a direita. Os blocos são numerados como se lê: da esquerda para a direita e de cima para baixo. O bloco 1 fica em cima à esquerda, o 5 no centro e o 9 embaixo à direita.

### Minissudokus

Para começar, ou para crianças, há dois tabuleiros menores que se jogam do mesmo jeito:

* **4 por 4:** números de 1 a 4, em 4 blocos de 2 por 2.
* **6 por 6:** números de 1 a 6, em 6 blocos de 2 linhas por 3 colunas. Há dois blocos em cada faixa de duas linhas: o 1 e o 2 em cima, o 3 e o 4 no meio, e o 5 e o 6 embaixo.

Se você pressionar um número maior do que o tabuleiro, soa o tom de erro e você ouve, por exemplo, “Neste sudoku os números vão de 1 a 4”.

## Começar um sudoku

1. Abra o menu do NVDA com NVDA+N.
2. Vá em Ferramentas e depois em MiSudokuAccesible.
3. Escolha “Novo sudoku...”.
4. Escolha o tamanho (4 por 4, 6 por 6 ou 9 por 9), o nível e as ajudas, e pressione OK.

A caixa de diálogo lembra a última escolha. Cada sudoku é criado na hora e tem uma única solução. Um sudoku médio ou difícil pode demorar alguns segundos: enquanto isso, você ouve “Preparando o sudoku...”.

### Níveis

Os níveis são medidos pelas técnicas necessárias para resolver o sudoku (veja “Dicas e técnicas”):

* **Fácil:** resolve-se com as três primeiras técnicas e começa com pelo menos 36 números colocados.
* **Médio:** precisa de pelo menos uma interseção.
* **Difícil:** precisa de pelo menos um par.

Nos minissudokus quase nunca são necessárias as técnicas difíceis, então há só dois níveis: **Fácil**, com mais números colocados, e **Médio**, com menos.

### Ajudas

A opção **Ajuda** da caixa de diálogo permite escolher o desafio:

* **Ligada:** dicas com P e Shift+P, e aviso quando um número entra em conflito.
* **Desligada:** sem dicas nem aviso de conflitos. Um número que entra em conflito é escrito sem aviso, como no papel. Verificar continua disponível no menu do tabuleiro.

Ler linhas, colunas e blocos (F, C e B), as anotações e F5 funcionam sempre: equivalem ao que se vê ao olhar o papel. Quando as ajudas estão desligadas, o título da janela diz “sem ajuda”.

## O que você ouve

* Célula com um número fixo: “Linha 3, coluna 5: 7, fixo”.
* Célula com um número que você escreveu: “Linha 3, coluna 5: 7”.
* Célula vazia: “Linha 3, coluna 5, vazia” e, se tiver anotações, “anotações 1, 4 e 7”.
* Ao passar para outro bloco, o número dele é acrescentado: “bloco 2”.

Se você preferir algo mais curto, nas opções pode escolher a forma curta: “L3C5: 7, fixo”.

## Teclas do tabuleiro

| Tecla | Ação |
|---|---|
| Setas | Mover-se pelas células |
| Home / End | Primeira ou última célula da linha |
| Tab / Shift+Tab | Próxima ou anterior célula vazia |
| 1 a 9 | Escrever esse número |
| Shift+1 a 9 | Colocar ou tirar esse número como anotação |
| Delete ou Backspace | Apagar o número da célula ou, se não tiver, suas anotações |
| Control+Z | Desfazer a última alteração |
| P | Dica curta: onde olhar e o que procurar |
| Shift+P | Dica completa: qual número vai, onde e por quê |
| N | Ler as anotações da célula |
| F | Ler a linha (F de fileira): quais números ela tem e quais faltam |
| C | Ler a coluna |
| B | Ler o bloco |
| F5 | Quantas células faltam |
| Aplicativos ou Shift+F10 | Menu do tabuleiro |
| Escape | Fechar o tabuleiro (o sudoku é guardado) |

As teclas podem ser mudadas no menu do NVDA, Preferências, Gestos de entrada, categoria MiSudokuAccesible. A lista completa, com as suas mudanças, está em “Atalhos de teclado”: no menu do tabuleiro, no das lições e em Ferramentas, MiSudokuAccesible.

## Ajudas durante o jogo

* **Conflitos:** se você escrever um número que já está na linha, na coluna ou no bloco dele, soa um tom e você ouve, por exemplo, “5, conflita com o 5 na linha”. Só se compara com os números que estão à vista, nunca com a solução.
* **Anotações:** ao escrever um número, essa anotação some sozinha das células da linha, da coluna e do bloco dele. Isso pode ser desativado nas opções.
* **Linhas, colunas e blocos completos:** quando um deles tem todos os números diferentes, soa um som curto e você ouve, por exemplo, “Linha 3 completa”.
* **Verificar** (no menu do tabuleiro): diz quantas células estão erradas, sem dizer quais.
* **Ao terminar:** toca uma melodia e é dito o tempo que você levou. O tempo é só informativo e conta apenas enquanto a janela do tabuleiro está ativa. Se for o seu melhor tempo naquele tamanho e nível, isso também é dito.

## Dicas e técnicas

As dicas não escrevem nada: elas dizem onde olhar ou qual número vai, e por quê, e você vai até a célula e escreve. São calculadas com o tabuleiro como está, mesmo que você não tenha feito anotações.

* **P, dica curta:** por exemplo, “Olhe no bloco 4: há um número que só cabe em um lugar”.
* **Shift+P, dica completa:** por exemplo, “O 7 só cabe na linha 5, coluna 2: as outras células vazias no bloco 4 já têm um 7 na linha, na coluna ou no bloco”.
* Se houver um número errado no tabuleiro, a dica diz primeiro onde ele está, porque a partir de um erro não se consegue raciocinar bem.
* Quando é preciso uma interseção ou um par, o número vai em um lugar e a razão está em outro. Por isso a dica curta nomeia os dois: “Você pode escrever um número na linha 3, mas antes é preciso uma interseção no bloco 2”. A completa diz primeiro onde o número vai e depois por quê.

As técnicas, da mais fácil à mais difícil:

1. **Último número:** a uma linha, coluna ou bloco falta só um número.
2. **Único lugar:** em uma linha, coluna ou bloco, um número só cabe em uma célula.
3. **Único número:** em uma célula só cabe um número, porque os outros já estão na linha, na coluna ou no bloco dela.
4. **Interseção:** em um bloco, um número só pode ir dentro de uma mesma linha (ou coluna). Então, no resto dessa linha, esse número não pode ir. Também ao contrário: se em uma linha um número só pode ir dentro de um bloco, ele não pode ir no resto do bloco.
5. **Par:** duas células de uma linha, coluna ou bloco só admitem os mesmos dois números. Então esses dois números não podem ir em nenhuma outra célula do grupo. Também ao contrário: se dois números só cabem nas mesmas duas células, essas células não podem ter outros números.

## Menu do tabuleiro

Abre-se com a tecla Aplicativos ou com Shift+F10:

* **Novo sudoku...:** começa outro sudoku. Se o atual tiver algo escrito, pede confirmação.
* **Verificar:** quantas células estão erradas.
* **Reiniciar:** apaga tudo o que você escreveu e volta ao começo, com o tempo em zero. Pede confirmação e não pode ser desfeito.
* **Atalhos de teclado:** as teclas desta janela.
* **Fechar o tabuleiro.**

## Salvamento automático

Cada alteração é guardada sozinha. Você pode fechar o tabuleiro com Escape, ou fechar o NVDA, sem perder nada. Para continuar, abra Ferramentas, MiSudokuAccesible, “Continuar o sudoku”.

## Sudoku do dia

Ferramentas, MiSudokuAccesible, “Sudoku do dia”: a cada dia há um novo sudoku de 9 por 9, o mesmo para todas as pessoas que usam esta versão do complemento. O nível depende do dia da semana: segunda e terça, fácil; quarta e quinta, médio; sexta, difícil; sábado e domingo, fácil.

* Antes de começar o de cada dia, pergunta-se se você quer jogá-lo com ajuda ou sem ajuda.
* Ele tem o seu próprio salvamento: se você o deixar pela metade, ao reabri-lo ele continua de onde estava, e o sudoku normal que você tenha começado não se perde.
* Só se pode jogar o de hoje. Quando você o resolve, é dito quantos dias seguidos você já completou. Se um dia você não o resolver, a contagem recomeça.
* Se você já o resolveu, ao abri-lo isso é lembrado e você é convidado a voltar amanhã.

## Aprender a jogar

Ferramentas, MiSudokuAccesible, “Aprender a jogar...”. É um curso guiado de 13 lições, pensado também para crianças. Por enquanto, as lições existem em espanhol e em português do Brasil: aparecem em português quando o NVDA está em português do Brasil, e em espanhol nos outros idiomas.

1. A lista mostra as lições, agrupadas em blocos, com o estado delas: pendente, em andamento ou concluída com suas estrelas. Escolha uma e pressione Iniciar.
2. Abre-se a explicação da lição. Leia-a com as setas ou deixe o NVDA lê-la, e pressione Iniciar.
3. Abre-se o tabuleiro com o primeiro exercício e você ouve a instrução. As teclas são as mesmas do jogo.

As lições:

* **Bloco A, Conhecendo o sudoku** (em 4 por 4): 1. As regras. 2. Linhas, colunas e blocos. 3. Escrever, apagar e anotações.
* **Bloco B, As técnicas** (em 6 por 6 e 9 por 9): 4. Último número. 5. Único lugar em um bloco. 6. Único lugar em linhas e colunas. 7. Único número. 8. As anotações como ajuda. 9. Interseção. 10. Par.
* **Bloco C, Hora de jogar:** sudokus inteiros, do começo ao fim. 11. Seu primeiro 4 por 4. 12. Seu primeiro 6 por 6. 13. Seu primeiro 9 por 9.

Nas lições:

* Um número que não vai não é escrito: soa o tom de erro e você ouve por quê, por exemplo “O 2 já está na linha 1. Tente outro”.
* **F2** repete a instrução do exercício e **Shift+F2**, a explicação da lição.
* **P** dá uma dica curta e **Shift+P**, uma completa.
* Cada exercício dá **3 estrelas** se você o faz sem dicas, **2** se usou a dica curta e **1** se usou a completa. Errar não tira estrelas. Nos sudokus inteiros do bloco C contam-se as dicas: 3 estrelas com nenhuma ou uma, 2 com até quatro e 1 com mais.
* Nos exercícios de técnicas não se diz a célula: diz-se onde olhar, porque encontrá-la é o exercício. Se você escrever em outra célula, ouve “Aqui não” e repete-se onde olhar.
* Os exercícios de interseção e de par têm dois passos, e o tabuleiro já traz as anotações feitas nas células que importam. No passo 1 explica-se o que se descarta e em qual célula tirar a anotação, por exemplo “Remova a anotação 7 na linha 3, coluna 7”: tire-a com Shift e o número. No passo 2, com a anotação tirada, aparece o número que você já pode escrever.
* Ao terminar um exercício, passa-se sozinho para o seguinte. Ao terminar a lição, o menu do tabuleiro tem “Próxima lição”, “Praticar esta lição”, “Lista de lições”, “Atalhos de teclado” e “Fechar a lição”.
* O progresso é guardado sozinho. Se você fechar uma lição pela metade, da próxima vez ela continua a partir do primeiro exercício pendente. Um sudoku inteiro do bloco C é guardado como estava, com as dicas que você pediu.

### Praticar

As lições do bloco B têm um botão **Praticar** na lista de lições, e também “Praticar esta lição” no menu do tabuleiro. Cada rodada tem 5 exercícios novos dessa técnica, criados na hora, então nunca acabam. O primeiro pode demorar alguns segundos para ficar pronto; os outros são preparados enquanto você joga.

Ao terminar a rodada, são ditas as estrelas conseguidas, de 15, e a sua melhor rodada. Para jogar outra, abra o menu do tabuleiro e escolha “Outra rodada de prática”.

## Minhas estatísticas

Ferramentas, MiSudokuAccesible, “Minhas estatísticas...”. Abrem-se em uma página que se lê como um site: H pula entre as seções, e há botões para copiar e fechar.

* **Sudokus resolvidos:** quantos de cada tamanho e nível, quantos deles sem ajuda, e o seu melhor tempo.
* **Sudoku do dia:** dias seguidos, recorde e total resolvidos.
* **Aprender a jogar:** lições concluídas, estrelas e a melhor prática de cada técnica.

## Opções

No menu do NVDA, Preferências, Configurações, categoria MiSudokuAccesible:

* **Falar a posição das células:** longa (“Linha 3, coluna 5”) ou curta (“L3C5”). As dicas sempre dizem a posição longa.
* **Ao escrever um número, remover essa anotação da linha, da coluna e do bloco** (ativado). As lições sempre fazem isso, porque é assim que ensinam.
* **Anunciar quando uma linha, coluna ou bloco estiver completo** (ativado).
* **Reproduzir sons** (ativado). Os tons de erro soam sempre.
* **Apagar meu progresso e estatísticas:** apaga o progresso do curso, a prática, os dias seguidos e as estatísticas. Pede confirmação. Os sudokus pela metade são mantidos.

## Sobre como este complemento foi feito

O MiSudokuAccesible nasceu porque eu sempre quis jogar sudoku para exercitar a concentração e a atenção, e porque queria que as pessoas com deficiência visual, e em especial crianças, pudessem aprender a jogá-lo plenamente com o NVDA. É o segundo jogo da minha coleção, depois do MiAjedrezAccesible.

Eu o desenvolvi com a assistência do Claude, um modelo de inteligência artificial da Anthropic. O Claude escreveu a maior parte do código seguindo minhas indicações, consultou a documentação e o código do NVDA e me propôs soluções técnicas. A direção e o critério foram inteiramente meus: o desenho funcional do complemento, o curso e a forma de ensinar, a experiência sonora, o comportamento com o leitor de telas e o descarte de características que não agregavam.

Cada versão, função, atalho e resposta de voz foi testada e validada por mim diretamente com o NVDA. Nenhuma função chegou à versão final sem a minha revisão e aprovação.

Conto isso porque acredito que é o honesto. Se você encontrar um erro, a responsabilidade é minha, e você me ajuda muito se me escrever para corrigi-lo.

## Autoria

Desenvolvido com amor por Wilmer Rodríguez Vega ([wilmer-rv.com](https://wilmer-rv.com)).

Tradução para o português do Brasil: brunowelber.

Para relatar um erro ou propor uma melhoria, escreva para contacto@wilmer-rv.com ou abra um relato na [página do complemento no GitHub](https://github.com/WilmerRv1989/MiSudokuAccesible/issues).

O MiSudokuAccesible é distribuído sob a licença GPL 2 ou posterior. Os sudokus são gerados no próprio complemento e os sons são próprios.
