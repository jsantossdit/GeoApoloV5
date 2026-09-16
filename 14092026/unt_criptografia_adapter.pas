unit unt_criptografia_adapter;

{
  GeoApolo - TCriptografiaAdapter
  Implementa ICriptografia delegando para as funcoes legadas
  criptografia() / decriptografia() da unit funcoes.pas.

  Isola a dependencia com "funcoes" neste unico adapter.
  Quando as funcoes forem migradas, basta trocar o corpo deste adapter.
}

interface

uses
  SysUtils,
  unt_logon_interfaces;

type

  TCriptografiaAdapter = class(TInterfacedObject, ICriptografia)
  private
    const CHAVE_CRIPT = 32;
    const CHAVE_DECRIPT_BANCO = 40;  // chave usada para senha do banco no registry
  public
    { ICriptografia }
    function Criptografar(const ATexto: string): string;
    function Decriptografar(const AHash: string): string;
  end;

  { Variante para a senha do banco (chave 40 usada no registry) }
  TCriptografiaBancoAdapter = class(TInterfacedObject, ICriptografia)
  public
    function Criptografar(const ATexto: string): string;
    function Decriptografar(const AHash: string): string;
  end;

implementation

uses
  funcoes;   // dependencia legada isolada aqui

{ TCriptografiaAdapter - chave 32 (senhas de usuario) }

function TCriptografiaAdapter.Criptografar(const ATexto: string): string;
begin
  Result := criptografia(32, ATexto);
end;

function TCriptografiaAdapter.Decriptografar(const AHash: string): string;
begin
  Result := decriptografia(32, AHash, '');
end;

{ TCriptografiaBancoAdapter - chave 40 (senha do registry) }

function TCriptografiaBancoAdapter.Criptografar(const ATexto: string): string;
begin
  // nao utilizado para banco, mas implementado por contrato
  Result := criptografia(40, ATexto);
end;

function TCriptografiaBancoAdapter.Decriptografar(const AHash: string): string;
begin
  Result := decriptografia(40, AHash, '');
end;

end.
