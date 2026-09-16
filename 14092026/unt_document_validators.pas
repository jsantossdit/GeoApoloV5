unit unt_document_validators;

{
  Validadores Puros de Documentos e Formatos (CPF, CNPJ, E-mail, CEP, Telefone).
  Totalmente desacoplados de VCL, forms e FireDAC.
}

interface

uses
  System.SysUtils, System.Classes, System.RegularExpressions;

type
  TDocumentValidators = class
  public
    class function ValidarCPF(const ACPF: string): Boolean; static;
    class function ValidarCNPJ(const ACNPJ: string): Boolean; static;
    class function ValidarEmail(const AEmail: string): Boolean; static;
    class function ValidarCEP(const ACEP: string): Boolean; static;
    class function LimparFormatacao(const ATexto: string): string; static;
    class function FormatarCPF(const ACPF: string): string; static;
    class function FormatarCNPJ(const ACNPJ: string): string; static;
    class function FormatarCEP(const ACEP: string): string; static;
  end;

implementation

class function TDocumentValidators.LimparFormatacao(const ATexto: string): string;
var
  I: Integer;
begin
  Result := '';
  for I := 1 to Length(ATexto) do
  begin
    if CharInSet(ATexto[I], ['0'..'9']) then
      Result := Result + ATexto[I];
  end;
end;

class function TDocumentValidators.ValidarCPF(const ACPF: string): Boolean;
var
  Digitos: string;
  I, Soma, Resto, Dig1, Dig2: Integer;
  TodosIguais: Boolean;
begin
  Digitos := LimparFormatacao(ACPF);
  if Length(Digitos) <> 11 then
    Exit(False);

  TodosIguais := True;
  for I := 2 to 11 do
  begin
    if Digitos[I] <> Digitos[1] then
    begin
      TodosIguais := False;
      Break;
    end;
  end;
  if TodosIguais then
    Exit(False);

  // Primeiro Dígito
  Soma := 0;
  for I := 1 to 9 do
    Soma := Soma + StrToInt(Digitos[I]) * (11 - I);
  Resto := (Soma * 10) mod 11;
  if Resto = 10 then
    Resto := 0;
  Dig1 := Resto;

  if StrToInt(Digitos[10]) <> Dig1 then
    Exit(False);

  // Segundo Dígito
  Soma := 0;
  for I := 1 to 10 do
    Soma := Soma + StrToInt(Digitos[I]) * (12 - I);
  Resto := (Soma * 10) mod 11;
  if Resto = 10 then
    Resto := 0;
  Dig2 := Resto;

  Result := StrToInt(Digitos[11]) = Dig2;
end;

class function TDocumentValidators.ValidarCNPJ(const ACNPJ: string): Boolean;
var
  Digitos: string;
  I, Soma, Resto, Dig1, Dig2: Integer;
  TodosIguais: Boolean;
  const Peso1: array[1..12] of Integer = (5,4,3,2,9,8,7,6,5,4,3,2);
  const Peso2: array[1..13] of Integer = (6,5,4,3,2,9,8,7,6,5,4,3,2);
begin
  Digitos := LimparFormatacao(ACNPJ);
  if Length(Digitos) <> 14 then
    Exit(False);

  TodosIguais := True;
  for I := 2 to 14 do
  begin
    if Digitos[I] <> Digitos[1] then
    begin
      TodosIguais := False;
      Break;
    end;
  end;
  if TodosIguais then
    Exit(False);

  // Primeiro Dígito
  Soma := 0;
  for I := 1 to 12 do
    Soma := Soma + StrToInt(Digitos[I]) * Peso1[I];
  Resto := Soma mod 11;
  if Resto < 2 then
    Dig1 := 0
  else
    Dig1 := 11 - Resto;

  if StrToInt(Digitos[13]) <> Dig1 then
    Exit(False);

  // Segundo Dígito
  Soma := 0;
  for I := 1 to 13 do
    Soma := Soma + StrToInt(Digitos[I]) * Peso2[I];
  Resto := Soma mod 11;
  if Resto < 2 then
    Dig2 := 0
  else
    Dig2 := 11 - Resto;

  Result := StrToInt(Digitos[14]) = Dig2;
end;

class function TDocumentValidators.ValidarEmail(const AEmail: string): Boolean;
var
  RegEx: TRegEx;
begin
  if Trim(AEmail) = '' then
    Exit(False);

  RegEx := TRegEx.Create('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
  Result := RegEx.IsMatch(Trim(AEmail));
end;

class function TDocumentValidators.ValidarCEP(const ACEP: string): Boolean;
var
  Digitos: string;
begin
  Digitos := LimparFormatacao(ACEP);
  Result := Length(Digitos) = 8;
end;

class function TDocumentValidators.FormatarCPF(const ACPF: string): string;
var
  D: string;
begin
  D := LimparFormatacao(ACPF);
  if Length(D) = 11 then
    Result := Format('%s.%s.%s-%s', [Copy(D, 1, 3), Copy(D, 4, 3), Copy(D, 7, 3), Copy(D, 10, 2)])
  else
    Result := ACPF;
end;

class function TDocumentValidators.FormatarCNPJ(const ACNPJ: string): string;
var
  D: string;
begin
  D := LimparFormatacao(ACNPJ);
  if Length(D) = 14 then
    Result := Format('%s.%s.%s/%s-%s', [Copy(D, 1, 2), Copy(D, 3, 3), Copy(D, 6, 3), Copy(D, 9, 4), Copy(D, 13, 2)])
  else
    Result := ACNPJ;
end;

class function TDocumentValidators.FormatarCEP(const ACEP: string): string;
var
  D: string;
begin
  D := LimparFormatacao(ACEP);
  if Length(D) = 8 then
    Result := Format('%s-%s', [Copy(D, 1, 5), Copy(D, 6, 3)])
  else
    Result := ACEP;
end;

end.
