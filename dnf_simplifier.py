# --- Красивый вывод ДНФ ---
def pretty_term(term):
	# Сортируем по имени переменной (без !)
	return ' & '.join(sorted(term, key=lambda x: (x.replace('!',''), x)))

def pretty_dnf(terms):
	if not terms:
		return '0'
	return ' v '.join(pretty_term(t) for t in terms)

# --- CLI ---
def main():
	print('Введите логическое выражение:')
	expr_str = input().strip()
	tokens = tokenize(expr_str)
	expr = parse(tokens)
	dnf_terms = to_dnf(expr)
	simplified = simplify_dnf(dnf_terms)
	print('Минимизированная ДНФ:')
	print(pretty_dnf(simplified))
# --- Упрощение ДНФ: поглощение и удаление дубликатов ---
def simplify_dnf(terms):
	# Удаляем дубликаты
	unique = []
	for t in terms:
		if t not in unique:
			unique.append(t)
	# Поглощение: если есть t1 ⊆ t2, то t2 удаляется
	result = []
	for t in unique:
		if not any((t2 < t) for t2 in unique):
			result.append(t)
	return result
# --- Построение ДНФ через логическое умножение ---
def to_dnf(expr):
	# Преобразует выражение в ДНФ (список конъюнкций, каждая — set литералов)
	if isinstance(expr, Var):
		return [set([expr.name])]
	if isinstance(expr, Not):
		if isinstance(expr.arg, Var):
			return [set(['!' + expr.arg.name])]
		# !(...) не поддерживается напрямую (ожидается КНФ)
		raise NotImplementedError('Отрицание сложных выражений не поддерживается')
	if isinstance(expr, And):
		# Декартово произведение всех аргументов
		dnfs = [to_dnf(arg) for arg in expr.args]
		result = [set()]
		for d in dnfs:
			new_result = []
			for r in result:
				for t in d:
					merged = r | t
					# Противоречие: x и !x
					names = set(l.replace('!','') for l in merged)
					for n in names:
						if n in merged and ('!' + n) in merged:
							break
					else:
						new_result.append(merged)
			result = new_result
		return result
	if isinstance(expr, Or):
		# Объединяем все ДНФ-термы
		result = []
		for arg in expr.args:
			result.extend(to_dnf(arg))
		return result
	raise NotImplementedError('Unknown expression type')
# Логический парсер: поддержка !, &, v, скобок
import re

class Expr:
	pass

class Var(Expr):
	def __init__(self, name):
		self.name = name
	def __repr__(self):
		return self.name

class Not(Expr):
	def __init__(self, arg):
		self.arg = arg
	def __repr__(self):
		return f'!{self.arg}'

class And(Expr):
	def __init__(self, args):
		self.args = args
	def __repr__(self):
		return '(' + ' & '.join(map(str, self.args)) + ')'

class Or(Expr):
	def __init__(self, args):
		self.args = args
	def __repr__(self):
		return '(' + ' v '.join(map(str, self.args)) + ')'

def tokenize(expr):
	# Разбиваем строку на токены
	tokens = re.findall(r'!|\(|\)|&|v|[a-zA-Z]\w*', expr)
	return tokens

def parse(tokens):
	# Рекурсивный спуск
	def parse_expr(index):
		def parse_factor(index):
			if tokens[index] == '(':  # скобки
				node, index = parse_expr(index+1)
				assert tokens[index] == ')'
				return node, index+1
			elif tokens[index] == '!':
				node, index = parse_factor(index+1)
				return Not(node), index
			else:
				node = Var(tokens[index])
				return node, index+1

		def parse_term(index):
			nodes = []
			node, index = parse_factor(index)
			nodes.append(node)
			while index < len(tokens) and tokens[index] == '&':
				node, index = parse_factor(index+1)
				nodes.append(node)
			if len(nodes) == 1:
				return nodes[0], index
			return And(nodes), index

		nodes = []
		node, index = parse_term(index)
		nodes.append(node)
		while index < len(tokens) and tokens[index] == 'v':
			node, index = parse_term(index+1)
			nodes.append(node)
		if len(nodes) == 1:
			return nodes[0], index
		return Or(nodes), index

	node, idx = parse_expr(0)
	if idx != len(tokens):
		raise ValueError('Unexpected token at the end')
	return node

if __name__ == '__main__':
	main()
