<?php


abstract class AbstractModel
{

    // Fetch Constant
    const FETCH_OBJ      = 1;
    const FETCH_JSON     = 2;
    const FETCH_KEYARRAY = 3;
    const FETCH_NUMARRAY = 4;
    const FETCH_XML      = 5;
    const FETCH_KEYVALUEARRAY = 6;

    // Like String Constant
    const LIKE_MATCHING_LEFT = 0;
    const LIKE_MATCHING_RIGHT =1;
    const LIKE_MATCHING_BOTH =2;
    const LIKE_MATCHING_PATTERN =3;

    // Encode/Decode String
    const STR_NORMAL = 0;
    const STR_UTF8 = 1;

    // Default Encode/Decode String
    const STR_DEFAULT = 1;

    /** @var  PDO */
    protected $pdo;

    /** @var  int */
    protected $id;

    /** @var  string */
    protected $tableName;

    /** @var string Condizioni Where aggiuntive per query base */
    protected $whereBase = "";

    /** @var string  Condizioni Order aggiuntive per query base*/
    protected $orderBase = "";

    /**
     *se settato esegue la limit con gli attributi passati<br/>
     * - Per ottenere i primi 10 elementi della query basterà passare '10'
     * - Per ottenere 10 elementi partendo dal terzo si passerà '3,10'
     *
     * @var integer
     */
    protected $limitBase = -1;
    /**
     * @var integer
     */
    protected $offsetBase = -1;

    /**
     * PdaAbstractModel constructor.
     *
     * @param PDO $pdo
     */
    function __construct(PDO $pdo)
    {
        $this->pdo = $pdo;
    }

    /**
     * Salvataggio dell'oggetto
     *
     * @param bool $forzaInsert se true salva l'oggetto settando anche la chiave primaria
     *
     * @return int
     */
    public function saveOrUpdate($forzaInsert = false)
    {
        if ($forzaInsert) {
            return $this->saveKeyArray(null, true);
        }
        else {
            return $this->saveKeyArray();
        }
    }

    /**
     * Funzione per la truncate della tabella
     *
     * @return  boolean
     */
    public final function truncateTable()
    {
        return $this->pdo->exec('TRUNCATE TABLE ' . $this->tableName);
    }

    /**
     * Funzione per la cancellazione di tutto il contenuto della tabella
     *
     * @return  boolean
     */
    public final function deleteTable()
    {
        return $this->pdo->exec('DELETE FROM ' . $this->tableName);
    }

    /**
     * Ritorna il nome Java Stile di una variabile
     *
     * @param $variabile
     *
     * @return string
     */
    protected final function creaNomeVariabile($variabile)
    {
        $variabile = ucwords(strtolower(str_replace("_", " ", $variabile)));
        $variabile = strtolower(substr($variabile, 0, 1)) . substr($variabile, 1, strlen($variabile));

        return str_replace(" ", "", $variabile);
    }

    //TODO: Risolvere problema update chiavi multiple
    /**
     * @param array $arrayValori
     * @param bool  $boolKey ser settato a true forza il salvataggio del nuovo recor anche se è presnete la chiave primaria
     * @return null|string
     */
    public function saveKeyArray($arrayValori = null, $boolKey = false)
    {
        if (!$arrayValori) $arrayValori = $this->createKeyArray();
        if ($boolKey) {
            $id = $this->issetPk($this->id);
            if ($id) {
                $this->id = $id;
            }
            else {
                $this->id = insertKeyArrayPdo($this->pdo,$this->tableName, $arrayValori);
            }
        }
        else if ($this->id) {
            //error_log("Update");
            updateKeyArrayPdo($this->pdo,$this->tableName, $arrayValori, $this->id);
        }
        else {
            //error_log("Insert");
            $this->id = insertKeyArrayPdo($this->pdo,$this->tableName, $arrayValori);
        }


        return $this->id;
    }

    /**
     * @param string $query
     * @param array|null parameters
     * @return int|string
     */
    protected function createResultValue($query, $parameters = null, $boolValue=false)
    {
        $val= queryPreparedPdo($this->pdo, $this->pdo->prepare($query), $parameters, "v");
        if($boolValue)
            return ($val > 0)? true : false;
        return $val;
    }


    /**
     * @param string $query
     * @param null $parametri
     * @param int $tipoRisultato
     * @param int $encodeType
     * @return array|string
     */
    protected function createResultArray($query, $parametri = null, $tipoRisultato = self::FETCH_OBJ, $encodeType = self::STR_DEFAULT)
    {
        $nomeClasse = get_class($this);
        $valoriPdo = queryPreparedPdo($this->pdo,$this->pdo->prepare($query), $parametri, "p");
        $arrayObj = array();
        switch ($tipoRisultato) {
            case self::FETCH_OBJ:
                while ($valori = $valoriPdo->fetch(PDO::FETCH_ASSOC)) {
                    $app = new $nomeClasse($this->pdo);
                    $app->createObjKeyArray($valori);
                    $arrayObj[] = $app;
                }
                $valoriPdo->closeCursor();

                return $arrayObj;
                break;
            case self::FETCH_JSON:
                while ($valori = $valoriPdo->fetch(PDO::FETCH_ASSOC)) {
                    $arrayObj[] = $this->encodeString($valori, $encodeType);
                }
                $valoriPdo->closeCursor();

                return json_encode($arrayObj);
                break;
            case self::FETCH_KEYARRAY:
                while ($valori = $valoriPdo->fetch(PDO::FETCH_ASSOC)) {
                    $arrayObj[] = $this->encodeArray($valori, $encodeType);
                }
                $valoriPdo->closeCursor();

                return $arrayObj;
                break;
            case self::FETCH_KEYVALUEARRAY:
                while ($valori = $valoriPdo->fetch(PDO::FETCH_NUM))
                {
                    $arrayObj[$valori[0]] = $this->utf8EncodeString($valori[1]);
                }
                $valoriPdo->closeCursor();
                return $arrayObj;
                break;
            case self::FETCH_NUMARRAY:
                while ($valori = $valoriPdo->fetch(PDO::FETCH_NUM)) {
                    $arrayObj[] = $this->encodeArray($valori, $encodeType);
                }
                $valoriPdo->closeCursor();

                return $arrayObj;
                break;
            case self::FETCH_XML:
                $xml = '<obj>';
                while ($valori = $valoriPdo->fetch(PDO::FETCH_ASSOC)) {
                    $xml .= "<$this->tableName>";
                    foreach ($valori as $chiave => $valore) {
                        $xml .= "<$chiave>$valore</$chiave>";
                    }
                    $xml .= "</$this->tableName>";
                }
                $xml = '</obj>';

                return $xml;
                break;
        }
        return null;
    }

    /**
     * @param $query
     * @param null $parametri
     * @param int $tipoRisultato
     * @param int $encodeType
     * @return array|null|string
     */
    protected function createResult($query, $parametri = null, $tipoRisultato = self::FETCH_OBJ,$encodeType=self::STR_DEFAULT)
    {
        $valori = queryPreparedPdo($this->pdo,$this->pdo->prepare($query), $parametri, "f");

        if (!$valori) {
            return;
        }

        switch ($tipoRisultato) {
            case self::FETCH_OBJ:
                foreach ($valori as $chiave => $valore) {
                    $variabile = $this->creaNomeVariabile($chiave);
                    $this->$variabile = $this->encodeString($valore, $encodeType);
                }
                break;
            case self::FETCH_JSON:
                return json_encode($this->encodeArray($valori, $encodeType));
                break;
            case self::FETCH_KEYARRAY:
                return $this->encodeArray($valori, $encodeType);
                break;
            case self::FETCH_NUMARRAY:
                //TODO: Da sistemare
                break;
            case self::FETCH_XML:
                $xml = "<$this->tableName>";
                foreach ($valori as $chiave => $valore) {
                    $xml .= "<$chiave>$valore</$chiave>";
                }
                $xml .= "</$this->tableName>";

                return $xml;
                break;
        }
        return null;
    }

    /**
     * Dato un oggetto Json istanzia la classe e la popola con i valori
     * @param $json
     * @param bool $flgObjJson
     */
    public function creaObjJson($json, $flgObjJson = false)
    {
        if ($flgObjJson) {
            $json = json_encode($json);
        }
        $json = json_decode($json, true);
        $this->createObjKeyArray($json);
    }

    /**
     * Restituisce la rappresentazione della classe in formato Json
     * @return string
     */
    public function getEmptyObjJson()
    {
        return json_encode(get_object_vars($this));
    }

    public function getEmptyDbJson()
    {
        return json_encode($this->getEmptyKeyArray());
    }

    /**
     * Restituisce la rappresentazione della classe in formato array
     * @return array
     */
    public function getEmptyObjKeyArray()
    {
        return get_object_vars($this);
    }

    /**
     * @param $input
     * @param $typeEncode
     * @return string
     */
    public function encodeString($input,$typeEncode) {
        if (is_string($input))
            switch($typeEncode){
                case self::STR_UTF8:
                    return utf8_encode($input);
                    break;
                default: return $input;
            }
        else
            return $input;
    }

    /**
     * @param $input
     * @param $typeEncode
     * @return string
     */
    public function decodeString($input,$typeEncode) {
        if (is_string($input))
            switch($typeEncode){
                case self::STR_UTF8:
                    return utf8_decode($input);
                    break;
                default: return $input;
            }
        else
            return $input;
    }

    /**
     * @param $input
     * @param $typeEncode
     * @return array
     */
    public function encodeArray($input,$typeEncode)
    {
        if (is_array($input)) {
            $app = array();
            foreach ($input as $key=>$value) {
                $app[$key]=$this->encodeString($value,$typeEncode);
            }
            return $app;
        } else
            return $input;
    }

    /**
     * @param $input
     * @param $typeEncode
     * @return array
     */
    public function decodeArray($input,$typeEncode)
    {
        if (is_array($input)) {
            $app = array();
            foreach ($input as $key=>$value) {
                $app[$key]=$this->decodeString($value,$typeEncode);
            }
            return $app;
        } else
            return $input;
    }

    /**
     * @param $input
     * @return string|int
     */
    public function encodeObj($input)
    {
        if (is_object($input)) {
            return $input;
            //todo sistempare
            /* $vars = array_keys(get_object_vars($input));

               foreach ($vars as $var) {
                   utf8_encode_deep($input->$var,$typeEncode);
               }*/
        } else
            return $input;
    }

    /**
     * @param string $string search string
     * @param int $likeMatching pattern for like matching
     */
    public function prepareLikeMatching($string, $likeMatching)
    {
        switch ($likeMatching) {
            case self::LIKE_MATCHING_LEFT :
                return '%' . $string;
            case self::LIKE_MATCHING_RIGHT :
                return $string . '%';
            case self::LIKE_MATCHING_BOTH :
                return '%' . $string . '%';
            default:
                return $string;
        }
    }

    /**
     * @param int $limit
     * @param int $offset
     * @return string
     */
    public function createLimitQuery($limit = -1,$offset = -1){
        $s='';
        if($limit > -1)
            $s.= ' LIMIT ' . $limit;
        elseif($this->limitBase > -1)
            $s.= ' LIMIT ' . $this->limitBase;

        if($offset > -1)
            $s.= ' OFFSET ' . $offset;
        elseif($this->offsetBase > -1)
            $s.= ' OFFSET ' . $this->offsetBase;

        return $s;
    }

    //------------------------------------------------------------------------------------------------------------------
    // Getter & Setter
    //------------------------------------------------------------------------------------------------------------------

    /**
     * @return PDO
     */
    public function getPdo()
    {
        return $this->pdo;
    }

    /**
     * @param PDO $pdo
     */
    public function setPdo($pdo)
    {
        $this->pdo = $pdo;
    }

    /**
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * @param int $id
     */
    public function setId($id)
    {
        $this->id = $id;
    }

    /**
     * @return string
     */
    public function getTableName()
    {
        return $this->tableName;
    }

    /**
     * @param string $tableName
     */
    public function setTableName($tableName)
    {
        $this->tableName = $tableName;
    }

    /**
     * @return string
     */
    public function getNomeTabella()
    {
        return $this->nomeTabella;
    }

    /**
     * @param string $nomeTabella
     */
    public function setNomeTabella($nomeTabella)
    {
        $this->nomeTabella = $nomeTabella;
    }

    /**
     * @return mixed
     */
    public function getWhereBase()
    {
        return $this->whereBase;
    }

    /**
     * @param mixed $whereBase
     */
    public function setWhereBase($whereBase)
    {
        $this->whereBase = $whereBase;
    }

    /**
     * @return string
     */
    public function getOrderBase()
    {
        return $this->orderBase;
    }

    /**
     * @param string $orderBase
     */
    public function setOrderBase($orderBase)
    {
        $this->orderBase = $orderBase;
    }

    /**
     * @return integer
     */
    public function getLimitBase()
    {
        return $this->limitBase;
    }

    /**
     * @param integer $limitBase
     */
    // public function setLimitBase(Integer $limitBase)
    public function setLimitBase( $limitBase)
    {
        $this->limitBase = $limitBase;
    }
    /**
     * @return integer
     */
    public function getOffsetBase()
    {
        return $this->offsetBase;
    }

    /**
     * @param integer $offsetBase
     */
    // public function setOffsetBase(Integer $offsetBase)
    public function setOffsetBase( $offsetBase)
    {
        $this->offsetBase = $offsetBase;
    }

    //------------------------------------------------------------------------------------------------------------------
    // Abstract
    //------------------------------------------------------------------------------------------------------------------

    /**
     * Transforms the object into a key array
     * @return array
     */
    public abstract function createKeyArray();

    /**
     * It transforms the keyarray in an object
     * @param array $keyArray
     */
    public abstract function createObjKeyArray(array $keyArray);

    public abstract function getEmptyKeyArray();

    /**
     * Return columns' list
     * @return string
     */
    public abstract function getListColumns();

    /**
     * DDL Table
     */
    public abstract function createTable();


    //------------------------------------------------------------------------------------------------------------------
    // Overrided
    //------------------------------------------------------------------------------------------------------------------

    /**
     * @param $id
     * @return int
     */
    private function issetPk($id)
    {
        return $this->createResultValue("SELECT ID FROM $this->tableName WHERE ID = ?", array($id));
    }

}