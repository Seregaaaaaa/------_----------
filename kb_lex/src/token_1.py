from .token_type import TokenType
class Token:
    def __init__(self, token_type, value, line, position):
        self.token_type = token_type
        if token_type == TokenType.INTEGER_CONST:
            self.value = self.str_to_int(value)
        elif token_type == TokenType.FLOAT_CONST:
            self.value = self.str_to_float(value)
        else:
            self.value = value
        self.line = line
        self.position = position

    def __str__(self):
        if self.value:
            return f"{self.token_type}: {self.value}"
        return f"{self.token_type}"
        
    def str_to_int(self, string):
        if not string:
            return 0
            
        result = 0
        
        for char in string:
            if not ('0' <= char <= '9'):
                raise ValueError(f"Недопустимый символ '{char}' в целом числе")
            
            digit = ord(char) - ord('0')  
            result = result * 10 + digit
            
        return result
    
    def str_to_float(self, string):

        if not string:
            return 0.0
            
        if '.' in string:
            whole_part, frac_part = string.split('.')
        else:
            whole_part, frac_part = string, "0"
            

        whole_value = self.str_to_int(whole_part)
        

        frac_value = 0
        for char in frac_part:
            if not ('0' <= char <= '9'):
                raise ValueError(f"Недопустимый символ '{char}' в дробной части числа")
                
            digit = ord(char) - ord('0')
            frac_value = frac_value * 10 + digit
            
        frac_digits = len(frac_part)
        frac_multiplier = 0.1
        for _ in range(1, frac_digits):
            frac_multiplier *= 0.1
            
        frac_value = frac_value * frac_multiplier
        
        result = whole_value + frac_value
        
        return result