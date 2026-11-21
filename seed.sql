USE moneyflow;

INSERT INTO despesas (descricao, valor, data, essencial, categoria_id) VALUES
-- Novembro de 2026
('Aluguel do quarto',       650.00, '2026-11-05', 'sim', (SELECT id FROM categorias WHERE nome = 'Moradia')),
('Conta de luz',             89.90, '2026-11-08', 'sim', (SELECT id FROM categorias WHERE nome = 'Moradia')),
('Compras do mês',          320.50, '2026-11-06', 'sim', (SELECT id FROM categorias WHERE nome = 'Alimentação')),
('Lanche com amigos',        42.00, '2026-11-09', 'nao', (SELECT id FROM categorias WHERE nome = 'Alimentação')),
('Passagem de ônibus',      110.00, '2026-11-03', 'sim', (SELECT id FROM categorias WHERE nome = 'Transporte')),
('Corrida de aplicativo',    23.50, '2026-11-12', 'nao', (SELECT id FROM categorias WHERE nome = 'Transporte')),
('Cinema',                   38.00, '2026-11-14', 'nao', (SELECT id FROM categorias WHERE nome = 'Lazer')),
('Curso de inglês',         120.00, '2026-11-10', 'sim', (SELECT id FROM categorias WHERE nome = 'Educação')),
('Farmácia',                 35.80, '2026-11-11', 'sim', (SELECT id FROM categorias WHERE nome = 'Saúde')),
('Streaming de filmes',      39.90, '2026-11-07', 'nao', (SELECT id FROM categorias WHERE nome = 'Assinaturas')),
('Streaming de música',      21.90, '2026-11-07', 'nao', (SELECT id FROM categorias WHERE nome = 'Assinaturas')),
('Guardado do mês',         200.00, '2026-11-15', 'sim', (SELECT id FROM categorias WHERE nome = 'Reserva de emergência')),
-- Outubro de 2026 (para testar a troca de mês)
('Aluguel do quarto',       650.00, '2026-10-05', 'sim', (SELECT id FROM categorias WHERE nome = 'Moradia')),
('Compras do mês',          298.70, '2026-10-06', 'sim', (SELECT id FROM categorias WHERE nome = 'Alimentação')),
('Show de música',          90.00,  '2026-10-18', 'nao', (SELECT id FROM categorias WHERE nome = 'Lazer'));

-- Conferência
SELECT d.id, d.descricao, d.valor, d.data, d.essencial, c.nome AS categoria
FROM despesas d
JOIN categorias c ON c.id = d.categoria_id
ORDER BY d.valor ASC;