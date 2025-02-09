# projeto-sistemas-distribuidos

Este é um projeto de compartilhamento de arquivos em rede P2P simples implementado em Python. Ele é composto por um servidor (`server.py`) e um cliente (`client.py`), ambos utilizando sockets para comunicação. O servidor gerencia os clientes e controla as informações dos arquivos disponíveis, enquanto os clientes podem enviar, buscar, excluir, e baixar arquivos de outros clientes na rede.

## Arquivos

- **server.py**: Responsável por gerenciar as conexões de clientes, processar comandos (como JOIN, CREATEFILE, DELETEFILE, SEARCH, LEAVE e LISTFILES) e manter um arquivo JSON com os dados de arquivos compartilhados.
- **client.py**: Interface de linha de comando para o cliente, permitindo que o usuário interaja com o servidor para enviar comandos como JOIN, REFRESH, SEARCH, GET e LEAVE.

## Funcionalidades

### No lado do servidor (`server.py`):

- **JOIN**: Permite que um cliente se conecte ao servidor.
- **CREATEFILE**: O cliente cria um arquivo no servidor com um nome e tamanho especificado.
- **DELETEFILE**: O cliente pode deletar um arquivo previamente enviado.
- **SEARCH**: O servidor pode buscar arquivos disponíveis por nome.
- **LEAVE**: Permite que um cliente se desconecte do servidor e remova seus arquivos.
- **LISTFILES**: Lista os arquivos de um cliente específico.

### No lado do cliente (`client.py`):

- **JOIN**: O cliente se conecta ao servidor.
- **REFRESH**: O cliente sincroniza sua lista de arquivos com o servidor.
- **SEARCH**: O cliente procura por arquivos no servidor.
- **GET**: O cliente baixa um arquivo de outro cliente na rede.
- **LEAVE**: O cliente se desconecta do servidor.
- **EXIT**: Sai do programa.

## Como rodar

### Requisitos

- Python 3.x
- Bibliotecas: `socket`, `threading`, `json`, `os`

### Rodando o servidor

1. Execute o servidor:

   ```bash
   python server.py
   ```

### Rodando o cliente

2. Execute o cliente:
   ```bash
   python client.py
   ```
