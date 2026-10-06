public function __construct(
        public readonly string $Operacao,
        public readonly ?string $Codigo,
        public readonly string $CPFCNPJ,
        public readonly string $Nome,
        public readonly string $DataFundacao,
        public readonly string $Genero,
        public readonly string $Endereco,
        public readonly string $NumeroEndereco,
        public readonly ?string $ComplementoEndereco,
        public readonly string $Bairro,
        public readonly string $Cep,
        public readonly string $CodigoCidade, 
        public readonly float $ValorContribuicao,
        public readonly ?string $NumeroBanco,    
        public readonly ?string $NumeroAgBancaria,
        public readonly ?string $NumeroContaCorrente,
        public readonly string $ComunicacaoEmail,
        public readonly array $Telefones,
        public readonly array $Emails,
        public readonly string $CodigoTipoCobranca,
        public readonly array $Categorias,
    ) {

        $this->TipoFisicaJuridica='Física';
    }
    
    public function toArray(): array
    {    
        return array_filter(
            get_object_vars($this),
            static fn ($value) => $value !== null
        );
    }

