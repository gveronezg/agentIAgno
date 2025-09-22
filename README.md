Anostações:...

Resposta:
"SKU, é o id que transita em todas as tabelas e é a chave.

se uma loja tem o mesmo sku em varias tabelas (algo esta errado) esse sku deve esta sendo usado para burlar a Auditoria de maneira sistêmica. 

exemplo:
SKU: 99999999
LOJA: 000

Vend. Cancelada: 02/01/2025
Ajuste: 12/02/2025
Devolução: 05/03/2025

o cara usou o mesmo SKU em variada transações, ele pegou um produto cancelado, ajustou ele no estoque e depois fez a devolução do mesmo.

maioria dos casos eles fazem o ajuste e em seguida faz a devolução do mesmo SKU.
mas para o Auditor chegar nessa analise demora muito em mededia o auditor analisa 100 -200 por visita em loja olhando SKU por SKU."

SELECT DISTINCT c.SKU
FROM cancelamentos c
JOIN ajustes a ON c.SKU = a.SKU
JOIN devolucoes d ON a.SKU = d.SKU
WHERE c.DATACANCELAMENTO >= '2025-01-01' AND c.DATACANCELAMENTO < '2025-02-01'
        AND a.DATA >= '2025-02-01' AND a.DATA < '2025-03-01'
        AND d.DATA_DEVOLUCAO >= '2025-03-01' AND d.DATA_DEVOLUCAO < '2025-04-01'
      ORDER BY c.SKU'