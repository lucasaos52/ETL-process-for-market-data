Creating a data lake using apache Airflow and AWS


A finalidade deste projeto é processar os preços históricos de compra/venda de ações e opções brasileiras, disponibilizando-os para uso futuro por outras aplicações.
Para conseguir isso, o Airflow é usado para automatizar o upload de dados para o S3, enquanto um pipeline ETL é empregado para construir e gerenciar um data lake hospedado no S3.
Além disso, um aplicativo Flask com Dash está incluído para mostrar como consumir esses dados.


Os pipelines de dados implementados são dinâmicos e construídos usando tarefas reutilizáveis que podem ser monitoradas e suportam preenchimentos suaves.

Os testes são realizados nos dados carregados e gerados para identificar quaisquer discrepâncias nos diretórios do S3.


** Conjunto de dados e pipelines **
Os conjuntos de dados de origem consistem em arquivos CSV contendo instantâneos de preços de mercado, volatilidade implícita de opções e outras metainformações,
como greves e datas de vencimento. Esses instantâneos de dados são supostamente salvos a cada 10 minutos, mas há vários arquivos ausentes e inconsistências nos números salvos.
Por exemplo, os preços às vezes são apresentados como "12,10" e outras vezes como "12,10". Os volumes podem aparecer como texto, como "10k12" em vez de 10120.


A etapa inicial é enviar esses dados para o S3, após o que eles são extraídos do S3 e processados usando o Spark, que é executado em um cluster EMR. 
Os dados são divididos em duas novas tabelas, cada uma contendo partes dos dados originais, com os números formatados incorretamente transformados apropriadamente.
Essas tabelas são então carregadas de volta para o S3 como arquivos parquet, particionados por ano, mês e dia.


Por fim, os diretórios do S3 criados são mapeados para as tabelas do Athena, permitindo que aplicativos externos consultem os dados usando SQL.
O Airflow orquestra todas essas etapas, utilizando dois DAGs diferentes e um sub-DAG para:

Carregue os dados no S3;
upload de dados

Processar os dados e criar tabelas de cotações e opções usando o sub-DAG;
data lake

Crie/atualize uma tabela Athena (sub-DAG).
athena-update



** Escalabilidade **
O conjunto de dados que está sendo manipulado consiste em mais de 1,5 milhão de linhas espalhadas por centenas de arquivos. 
Consequentemente, a pilha de tecnologia mencionada foi escolhida para lidar com tarefas de big data de forma eficaz e facilitar o gerenciamento das complexidades de pipeline apresentadas.

Os clusters EMR, onde o Spark é executado, são facilmente escaláveis. O S3, que hospeda o data lake, e o Athena, usado para consultar os dados, são sem servidor e aumentam e diminuem de acordo com a demanda. 
Se os dados aumentassem 100 vezes, seria necessário apenas ajustar a configuração do script para aumentar o cluster EMR de acordo. Da mesma forma, se o banco de dados precisasse ser acessado por 100 ou mais indivíduos,
 o Athena poderia lidar com isso perfeitamente.

Além disso, cada etapa nos DAGs possui dependências que devem ser executadas com êxito antes delas. O Airflow gerencia essas dependências com eficiência, 
facilitando a depuração, salvando logs para cada etapa e fornecendo progresso de execução preciso ou informações de falha. 
O Airflow também assume o papel de crontabs, permitindo que os pipelines sejam programados para serem executados em horários específicos do dia, como todos os dias às 7h.

Instalaçãop

Para configurar o ambiente Python para executar o código neste repositório, siga estas etapas:

1. Crie um novo ambiente usando Anaconda com Python 3.6:
$ conda create --name ngym36 python=3.6

2. Ative o ambiente recém-criado:
concha
Copiar código
$ fonte ativar ngym36

3. Instale as dependências necessárias executando o seguinte comando no diretório de projeto de nível superior (o diretório que contém este arquivo LEIA-ME):
concha
Copiar código
$ pip install -r requisitos.txt


** Executando o Código **
Para executar o código e executar os processos ETL, execute as seguintes etapas:

1. Abra um terminal ou janela de comando e navegue até o diretório de projeto de nível superior.

2. Use o Airflow para orquestrar os processos ETL e iniciar um cluster EMR para executar trabalhos do Spark, processar os dados e salvar os resultados em buckets S3. Comece renomeando o arquivo confs/dpipe.template.cfg para confs/dpipe.cfg. Preencha os valores ACCESS_KEY_ID e SECRET_ACCESS_KEY na seção AWS do arquivo de configuração. Em seguida, execute os seguintes comandos:

concha
Copiar código
$ . scripts/download-data.sh
$ python iac.py -i
$ . scripts/setup-airflow.sh
$ python iac.py -a
$ . scripts/start-airflow.sh
Nota: Alguns erros podem aparecer durante a execução, mas não se preocupe com eles.

Depois de executar os comandos acima, abra seu navegador da Web e navegue até http://localhost:3000. Na IU do Airflow, ative o upload_raw_data DAG. Isso criará os depósitos S3 necessários e carregará todos os dados baixados anteriormente. Depois que o upload_raw_data DAG for concluído, ative o create_datalake DAG para iniciar o processo ETL. Você pode clicar no nome do DAG para monitorar as etapas de execução.

Por fim, quando terminar, limpe seus recursos executando os seguintes comandos:

concha
Copiar código
$ . scripts/stop-ariflow.sh
$ python app.py
Usando o aplicativo
Depois que o aplicativo estiver em execução, você poderá explorar o data lake criado acessando o aplicativo Dash. Como alternativa, você pode usar o bloco de anotações Jupyter local athena-query-local para ver alguns exemplos de uso da API Athena.

Comandos Adicionais
O script iac.py fornece comandos adicionais para ajudar a explorar a funcionalidade EMR, se desejado. As seguintes bandeiras estão disponíveis:

-e: inicia um cluster EMR
-s: verifique o status de um cluster EMR
-d: encerrar um cluster EMR
Use o sinalizador -h para ver a descrição e as instruções de uso de cada comando.

Esquemas de tabela
Os esquemas de tabela para os dois conjuntos de dados são os seguintes:

Citações:

data int: Inteiro. Data e hora no formato AAAAMMDDHHmm.
marcador: String. Nome do instrumento, que pode ser uma opção ou um ticker da bolsa.
last_close: Flutuar. Preço de fechamento da sessão anterior.
aberto: Flutuar. Preço de abertura da sessão atual.
máx.: Flutuar. Preço máximo negociado na sessão atual.
min: Flutuar. Preço mínimo negociado na sessão atual.
último: Flutuar. Preço máximo negociado na sessão atual.
qty_bid: inteiro. Quantidade total no melhor preço de oferta.
lance: Flutuar. Melhor preço de lance.
pergunte: Flutue. Melhor preço de venda.
qty_ask: inteiro. Quantidade total no melhor preço de venda.
num_trades: Float. Número de negociações na sessão atual.
qty_total: Flutuante. Quantidade total negociada no atual

