"""Manual translations for Module_en.trans — entries that weren't auto-migrated.

Terminology conventions (aligned with old dict glossary):
- Сессия → Session
- Ключ → Key (в значениях пишу "key", не "Key_")
- Значение → Value (в полях), value (как существительное)
- Кодировка → Encoding
- Заголовки → Headers
- Тело → Body
- Код состояния → Status code
- Аутентификация → Authentication
- Сервер → host (в старом словаре так) / server (где уместно)
- Платформа → Platform
- BSP/БСП → SSL (Standard Subsystems Library)
- Произвольный → Arbitrary
- Неопределено → Undefined / True → True / Ложь → False
"""

TR = {
    # Query parameter sub-fields (Get)
    "Method.Get.Param.ПараметрыЗапроса.Значение.Type.0.Description":
        "URL parameter value",
    "Method.Get.Param.ПараметрыЗапроса.Значение.Type.1.Description":
        "builds a string from multiple parameters\\: key\\=value1&key\\=value2 etc.",
    "Method.Get.Param.ПараметрыЗапроса.Ключ.Description":
        "URL parameter key.",

    # HMAC
    "Method.HMAC.Param.Ключ.Description":
        "secret key.",

    # JsonToObject
    "Method.JsonВОбъект.Description":
        "Converts JSON to Object.",
    "Method.JsonВОбъект.Param.Json.Description":
        "JSON-formatted data.",
    "Method.JsonВОбъект.Param.Кодировка.Description":
        "JSON text encoding. Default value - utf-8.",
    "Method.JsonВОбъект.Param.ПараметрыПреобразования.Description":
        "JSON conversion parameters",
    "Method.JsonВОбъект.Param.ПараметрыПреобразования.ИменаСвойствСоЗначениямиДата.Description":
        "JSON property names\\nfor which date restoration from string should be called.",
    "Method.JsonВОбъект.Param.ПараметрыПреобразования.ИмяФункцииВосстановления.Description":
        "specifies the name of the function that will be called when reading\\neach property and must have the following parameters",
    "Method.JsonВОбъект.Param.ПараметрыПреобразования.ИмяФункцииВосстановления.Значение.Description":
        "value of a serializable type",
    "Method.JsonВОбъект.Param.ПараметрыПреобразования.ИмяФункцииВосстановления.Свойство.Description":
        "specified only when reading JSON objects",
    "Method.JsonВОбъект.Param.ПараметрыПреобразования.ПрочитатьВСоответствие.Description":
        "if True, the JSON object will be read into a Map,\\notherwise into a Structure.",
    "Method.JsonВОбъект.Param.ПараметрыПреобразования.ФорматДатыJSON.Description":
        "specifies the deserialization format of JSON object dates.",
    "Method.JsonВОбъект.Return.Description":
        "value deserialized from JSON.",

    # Mkcol
    "Method.Mkcol.Description":
        "Sends a MKCOL request",
    "Method.Mkcol.Param.URL.Description":
        "HTTP URL to send the request to.",

    # RestoreJson
    "Method.ВосстановлениеJson.Description":
        "Restores a value of a type whose deserialization is not supported.",
    "Method.ВосстановлениеJson.Param.Значение.Description":
        "value to restore.",
    "Method.ВосстановлениеJson.Param.Свойство.Description":
        "name of the property whose value needs to be restored.",
    "Method.ВосстановлениеJson.Param.ТипыСвойств.Description":
        "property types to restore.\\n* Key - String - property name. Equals the value of the Property parameter.",
    "Method.ВосстановлениеJson.Return.Description":
        "restored value.",

    # CallHTTPMethod comment
    "Method.ВызватьHTTPМетод.Comment.INFO\\:\\ по\\ хорошему\\ аутентификацию\\ нужно\\ привести\\ к\\ новых\\ параметрам,\\ но\\ пока\\ будем\\ игнорировать\\..Description":
        "INFO\\: in general, authentication should be aligned with new parameters, but we'll ignore it for now.",

    # CallMethod
    "Method.ВызватьМетод.Description":
        "Sends data to a specific URL with a specific HTTP verb.",
    "Method.ВызватьМетод.Param.URL.Description":
        "HTTP URL to send the request to.",
    "Method.ВызватьМетод.Param.Метод.Description":
        "HTTP request verb name.",
    "Method.ВызватьМетод.Return.Cookies.Description":
        "cookies received from host.",
    "Method.ВызватьМетод.Return.Description":
        "a response for the executed request",
    "Method.ВызватьМетод.Return.URL.Description":
        "final request URL.",
    "Method.ВызватьМетод.Return.ВремяВыполнения.Description":
        "execution response duration in milliseconds.",
    "Method.ВызватьМетод.Return.Заголовки.Description":
        "HTTP response headers.",
    "Method.ВызватьМетод.Return.КодСостояния.Description":
        "response status code.",
    "Method.ВызватьМетод.Return.Кодировка.Description":
        "response text encoding.",
    "Method.ВызватьМетод.Return.Тело.Description":
        "response body.",
    "Method.ВызватьМетод.Return.ЭтоПостоянныйРедирект.Description":
        "permanent redirect flag.",
    "Method.ВызватьМетод.Return.ЭтоРедирект.Description":
        "redirect flag.",

    # WriteGZip
    "Method.ЗаписатьGZip.Description":
        "Writes data to a GZip archive.",
    "Method.ЗаписатьGZip.Param.Данные.Description":
        "source data.",
    "Method.ЗаписатьGZip.Return.Description":
        "GZip-packed data.",

    # FillListWithFilteredCookies comment
    "Method.ЗаполнитьСписокОтфильтрованнымиCookies.Comment.INFO\\:\\ проверка\\ срока\\ действия\\ игнорируется\\ (Cookie\\.Значение\\.СрокДействия)\\nINFO\\:\\ проверка\\ порта\\ игнорируется.Description":
        "INFO\\: expiration check is ignored (Cookie.Value.Expires)\\nINFO\\: port check is ignored",

    # ConnectionIdentifier comment
    "Method.ИдентификаторСоединения.Comment.Для\\ упрощения\\ будет\\ считать,\\ что\\ сертификаты\\ в\\ рамках\\ сессии\\ не\\ меняются.Description":
        "For simplicity, we'll assume that certificates do not change within a session",

    # AsJson
    "Method.КакJson.Description":
        "Returns host response as deserialized JSON value.",
    "Method.КакJson.Param.ПараметрыПреобразованияJSON.Description":
        "If False, objects will be read into a Structure.\\n* JSONDateFormat - JSONDateFormat - the format in which the date is represented in the string being converted.\\n* PropertiesNamesWithDateValues -  Array, String - JSON property names,\\nfor which date restoration from string should be called.\\n* RestoreFunctionName - String - specifies the name of the function that will be called when reading\\neach property and must have the following parameters\\:\\n** Property - String - specified only when reading JSON objects\\n** Value - Arbitrary - value of a serializable type\\n** AdditionalParameters - Arbitrary",
    "Method.КакJson.Return.Description":
        "host response as deserialized JSON value.\\nIf ConversionParameters.ReadToMap \\= True (by default).\\nStructure - If ConversionParameters.ReadToMap \\= False.",

    # AsXDTO
    "Method.КакXDTO.Description":
        "Returns host response as XDTO.",
    "Method.КакXDTO.Param.Кодировка.Description":
        "Contains the input stream encoding.\\n See details of the method XMLReader.OpenStream in the Syntax Assistant",
    "Method.КакXDTO.Param.НаборСхемXML.Description":
        "An XML schema set used for validation of the document being read.\\nIf a schema set is specified but not validated and XML document validation is enabled, the schema set is validated.\\n See details of the method XMLReader.OpenStream in the Syntax Assistant",
    "Method.КакXDTO.Param.ПараметрыЧтенияXML.Description":
        "Parameters for reading XML data\\n See details of the method XMLReader.OpenStream in the Syntax Assistant",
    "Method.КакXDTO.Return.Description":
        "Return value can have any type that supports serialization to XDTO.",

    # AsBinaryData
    "Method.КакДвоичныеДанные.Description":
        "Returns host response as binary data.",
    "Method.КакДвоичныеДанные.Return.Description":
        "host response as binary data.",

    # AsException
    "Method.КакИсключение.Description":
        "Returns host response as text intended for use in Raise.",
    "Method.КакИсключение.Param.ТекстДляПользователя.Description":
        "Reason explanation text for the user.",
    "Method.КакИсключение.Return.Description":
        "host response as exception text.",

    # AsText
    "Method.КакТекст.Description":
        "Returns host response as text.",
    "Method.КакТекст.Param.Кодировка.Description":
        "contains text encoding.\\nIf value is empty, the encoding is taken from Response.Encoding.",
    "Method.КакТекст.Return.Description":
        "host response as text.",

    # HTTPStatusCodes
    "Method.КодыСостоянияHTTP.Description":
        "Returns a structure of named HTTP status codes.",
    "Method.КодыСостоянияHTTP.Return.Description":
        "named HTTP status codes.",

    # NewAuthenticationAWS4
    "Method.НоваяАутентификацияAWS4.Description":
        "AWS4-HMAC-SHA256 authentication constructor",
    "Method.НоваяАутентификацияAWS4.Return.ИдентификаторКлючаДоступа.Description":
        "access key identifier (AccessKey).",
    "Method.НоваяАутентификацияAWS4.Return.Регион.Description":
        "region being connected to.",
    "Method.НоваяАутентификацияAWS4.Return.СекретныйКлюч.Description":
        "secret key (SecretKey).",
    "Method.НоваяАутентификацияAWS4.Return.Сервис.Description":
        "service being connected to.",
    "Method.НоваяАутентификацияAWS4.Return.Тип.Description":
        "Authentication type code. Always \"AWS4-HMAC-SHA256\".",

    # NewAuthenticationBasic
    "Method.НоваяАутентификацияBasic.Description":
        "Basic authentication constructor",
    "Method.НоваяАутентификацияBasic.Return.Пароль.Description":
        "user password.",
    "Method.НоваяАутентификацияBasic.Return.Пользователь.Description":
        "user name.",

    # NewAuthenticationBearer
    "Method.НоваяАутентификацияBearer.Description":
        "Bearer authentication constructor",
    "Method.НоваяАутентификацияBearer.Return.Тип.Description":
        "Authentication type code. Always \"Bearer\".",
    "Method.НоваяАутентификацияBearer.Return.Токен.Description":
        "Bearer token.",

    # NewAuthenticationDigest
    "Method.НоваяАутентификацияDigest.Description":
        "Digest authentication constructor",
    "Method.НоваяАутентификацияDigest.Return.Пароль.Description":
        "user password.",
    "Method.НоваяАутентификацияDigest.Return.Пользователь.Description":
        "user name.",
    "Method.НоваяАутентификацияDigest.Return.Тип.Description":
        "Authentication type code. Always \"Digest\".",

    # NewAuthenticationOS
    "Method.НоваяАутентификацияОС.Description":
        "Operating system authentication constructor",
    "Method.НоваяАутентификацияОС.Return.ИспользоватьАутентификациюОС.Description":
        "enables the use of NTLM or Negotiate authentication.",

    # NewParameters (huge)
    "Method.НовыеПараметры.Description":
        "Additional parameters constructor",
    "Method.НовыеПараметры.Return.Description":
        "value restoration.\\n** AdditionalRestoreFunctionParameters - Arbitrary - specifies additional parameters that\\nwill be passed to the value restoration function.\\n** PropertyNamesForRestorationProcessing - Array - specifies an array of JSON property names for which\\nthe restoration function will be called.\\n** MaxNesting - Number - specifies the maximum nesting level of the JSON object.\\n* JSONWriteParameters - JSONWriteParameters - used when writing a JSON object.\\n* Data - String, BinaryData - arbitrary data to send in the request.\\n- Structure, Map - form fields to send in the request\\:\\n** Key - String - field name.\\n** Value - String - field value.\\n* Files -\\n, Array Of\\n- files to send\\n* MaxRetryCount - Number - number of connection/request send retries.\\nAn exponentially growing delay is applied between retries.\\nBut if the status code is one of 413, 429, 503\\nand the response has a Retry-After header,\\nthe delay is derived from this header's value\\nDefault value\\: 0 - retries are not performed.\\n* MaxRetryTime - Number - maximum total time (in seconds) for sending the request including retries.\\nDefault value\\: 600.\\n* ExponentialBackoffFactor - Number - coefficient of exponential delay change.\\n1 produces a sequence of delays\\: 1, 2, 4, 8, etc.\\n2 produces a sequence of delays\\: 2, 4, 8, 16, etc.\\n...\\nDefault value\\: 1.\\n* RetryForStatusCodes - Undefined - retries are performed for status codes >\\= 500.\\n- Array - retries are performed for specific status codes.\\nDefault value\\: Undefined.",

    # NewResponse
    "Method.НовыйОтвет.Comment.Сетевая\\ ошибка\\ (>500).Description":
        "Network error (>500)",
    "Method.НовыйОтвет.Description":
        "Response package of an HTTP method call result.",
    "Method.НовыйОтвет.Return.Description":
        "String - HTTP request verb name\\n* URL - String - final request URL.",

    # NewFileToSend
    "Method.НовыйОтправляемыйФайл.Description":
        "Constructor of the file-to-send description.",
    "Method.НовыйОтправляемыйФайл.Param.Данные.Description":
        "file binary data.",
    "Method.НовыйОтправляемыйФайл.Param.Имя.Description":
        "form field name.",
    "Method.НовыйОтправляемыйФайл.Param.ИмяФайла.Description":
        "file name.",
    "Method.НовыйОтправляемыйФайл.Param.Тип.Description":
        "file MIME type",
    "Method.НовыйОтправляемыйФайл.Return.Данные.Description":
        "file binary data.",
    "Method.НовыйОтправляемыйФайл.Return.Заголовки.Description":
        "HTTP request headers.",
    "Method.НовыйОтправляемыйФайл.Return.Имя.Description":
        "form field name.",
    "Method.НовыйОтправляемыйФайл.Return.ИмяФайла.Description":
        "file name.",
    "Method.НовыйОтправляемыйФайл.Return.Тип.Description":
        "file MIME type.",

    # ObjectToJson
    "Method.ОбъектВJson.Description":
        "Converts an Object to JSON.",
    "Method.ОбъектВJson.Param.Объект.Description":
        "data to convert to JSON.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.Description":
        "JSON conversion parameters",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ИспользоватьДвойныеКавычки.Description":
        "specifies whether JSON property names will be\\nwritten in double quotes.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ПереносСтрок.Description":
        "specifies the line-break method\\nto be used when writing JSON data.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.СимволыОтступа.Description":
        "specifies the indent characters used when writing JSON data.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ЭкранированиеСимволов.Description":
        "specifies the character escaping (replacement) method\\nto use when writing JSON data.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ЭкранироватьАмперсанд.Description":
        "specifies whether the ampersand \"&\" character will be escaped when writing.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ЭкранироватьОдинарныеКавычки.Description":
        "specifies whether single quotes will be escaped.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ЭкранироватьРазделителиСтрок.Description":
        "specifies whether the line separators\\nU+2028 (line-separator) and U+2029 (page-separator) will be escaped.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ЭкранироватьСлеш.Description":
        "specifies whether the slash will be escaped when writing the value.",
    "Method.ОбъектВJson.Param.ПараметрыЗаписи.ЭкранироватьУгловыеСкобки.Description":
        "specifies whether the \"<\" and \">\" characters will be escaped when writing.",
    "Method.ОбъектВJson.Param.ПараметрыПреобразования.Description":
        "* JSONDateWriteMode - JSONDateWriteMode - specifies how dates are written in JSON format.\\n* ConversionFunctionName - String - a function called for all properties\\nwhose type does not support automatic serialization to JSON.\\nThe function must be exported and have the following parameters\\:\\n** Property - String - a data structure property that cannot be\\nautomatically serialized to JSON.\\n** Value - String - the value of a data structure property that\\ncannot be automatically serialized to JSON.\\n** AdditionalParameters - Arbitrary - this parameter will receive\\nAdditionalConversionFunctionParameters.\\n** Cancel - Boolean - cancels the property-write operation.\\nReturn value of the function\\:\\nArbitrary - conversion result.\\n* ConversionFunctionModule - Arbitrary - module where the ConversionFunctionName function is defined.\\n* AdditionalConversionFunctionParameters - Arbitrary - parameters that will be passed\\nto the ConversionFunctionName function.",
    "Method.ОбъектВJson.Return.Description":
        "object in JSON format.",

    # OverrideMethod comment
    "Method.ПереопределитьМетод.Comment.Поведение\\ браузеров.Description":
        "Browser behavior",

    # PrepareAuthenticationBearer comment
    "Method.ПодготовитьАутентификациюBearer.Comment.Токен\\ не\\ заполнен\\..Description":
        "Token is not set.",

    # PrepareHeaderDigest comment
    "Method.ПодготовитьЗаголовокDigest.Comment.INFO\\:\\ auth-int\\ не\\ реализовано.Description":
        "INFO\\: auth-int is not implemented",

    # HTTPStatusCodePresentation
    "Method.ПредставлениеКодаСостоянияHTTP.Description":
        "Returns a text representation of the given HTTP status code.",
    "Method.ПредставлениеКодаСостоянияHTTP.Param.КодСостояния.Description":
        "HTTP status code for which to obtain a text representation.",
    "Method.ПредставлениеКодаСостоянияHTTP.Return.Description":
        "text representation of the HTTP status code.",

    # ConvertJson
    "Method.ПреобразованиеJson.Comment.Если\\ значение\\ не\\ поддерживает\\ сериализацию\\ в\\ JSON,\\ то\\ будет\\ выброшено\\ исключение.Description":
        "If the value does not support serialization to JSON, an exception will be raised",
    "Method.ПреобразованиеJson.Description":
        "Converts a value to a type whose serialization is supported.",
    "Method.ПреобразованиеJson.Param.ДополнительныеПараметры.Description":
        "additional parameters specified in the WriteJSON method call.",
    "Method.ПреобразованиеJson.Param.Значение.Description":
        "source value.",
    "Method.ПреобразованиеJson.Param.Отказ.Description":
        "cancellation of the property write.",
    "Method.ПреобразованиеJson.Param.Свойство.Description":
        "property name, if writing a structure or map.",
    "Method.ПреобразованиеJson.Return.Description":
        "see types in WriteJSON.",

    # Pause comment
    "Method.Приостановить.Comment.Когда-нибудь\\ в\\ платформе\\ сделают\\ паузу\\ и\\ это\\ можно\\ будет\\ выкинуть.Description":
        "Someday the platform will implement pause and this can be removed",

    # ReadGZip
    "Method.ПрочитатьGZip.Description":
        "Reads data from a GZip archive.",
    "Method.ПрочитатьGZip.Param.СжатыеДанные.Description":
        "GZip-packed data.",
    "Method.ПрочитатьGZip.Return.Description":
        "unpacked data.",

    # ReadZip comment
    "Method.ПрочитатьZip.Comment.Игнорируем\\ проверку\\ целостности\\ архива,\\ просто\\ читаем\\ результат.Description":
        "Ignoring the archive integrity check, just reading the result",

    # ParseURL
    "Method.РазобратьURL.Description":
        "Returns a structured representation of a URL.",
    "Method.РазобратьURL.Param.URL.Description":
        "HTTP URL to send the request to.",
    "Method.РазобратьURL.Return.Description":
        "URL structure",
    "Method.РазобратьURL.Return.Аутентификация.Description":
        "authentication parameters",
    "Method.РазобратьURL.Return.Аутентификация.Пароль.Description":
        "user password.",
    "Method.РазобратьURL.Return.Аутентификация.Пользователь.Description":
        "user name.",
    "Method.РазобратьURL.Return.ПараметрыЗапроса.Description":
        "request parameters passed to the server in the URL (the part after ?)",
    "Method.РазобратьURL.Return.ПараметрыЗапроса.Значение.Type.0.Description":
        "URL parameter value;",
    "Method.РазобратьURL.Return.ПараметрыЗапроса.Значение.Type.1.Description":
        "parameter values (key\\=value1&key\\=value2).",
    "Method.РазобратьURL.Return.ПараметрыЗапроса.Ключ.Description":
        "URL parameter key.",
    "Method.РазобратьURL.Return.Порт.Description":
        "server port.",
    "Method.РазобратьURL.Return.Путь.Description":
        "resource address on the server.",
    "Method.РазобратьURL.Return.Сервер.Description":
        "server address.",
    "Method.РазобратьURL.Return.Схема.Description":
        "server access scheme (http, https).",
    "Method.РазобратьURL.Return.Фрагмент.Description":
        "URL part after \\#.",

    # CreateSession
    "Method.СоздатьСессию.Description":
        "Creates an object to store session parameters.",
    "Method.СоздатьСессию.Return.*.Description":
        "Token - String - token.\\nIf Type \\= AWS4-HMAC-SHA256\\:",
    "Method.СоздатьСессию.Return.Cookies.Description":
        "cookies storage.",
    "Method.СоздатьСессию.Return.Description":
        "session parameters",
    "Method.СоздатьСессию.Return.Аутентификация.Description":
        "request authentication parameters.",
    "Method.СоздатьСессию.Return.Заголовки.Description":
        "HTTP request headers.",
    "Method.СоздатьСессию.Return.Значение.Type.0.Description":
        "URL parameter value",
    "Method.СоздатьСессию.Return.Значение.Type.1.Description":
        "builds a string from multiple parameters\\: key\\=value1&key\\=value2 etc.",
    "Method.СоздатьСессию.Return.КлиентскийСертификатSSL.Description":
        "Default value\\: Undefined.",
    "Method.СоздатьСессию.Return.Ключ.Description":
        "URL parameter key.",
    "Method.СоздатьСессию.Return.МаксимальноеКоличествоПеренаправлений.Description":
        "maximum redirect count. Loop protection.\\nDefault value\\: 30",
    "Method.СоздатьСессию.Return.ПараметрыЗапроса.Description":
        "parameters to send in the URL (the part after ?)",
    "Method.СоздатьСессию.Return.ПроверятьSSL.Type.0.Description":
        "False - server certificate verification is not performed.",
    "Method.СоздатьСессию.Return.ПроверятьSSL.Type.1.Description":
        "the value of CACertificatesOS is used.",
    "Method.СоздатьСессию.Return.ПроверятьSSL.Type.2.Description":
        "See CACertificatesFile.\\nDefault value\\: True.",
    "Method.СоздатьСессию.Return.Прокси.Description":
        "proxy parameters to be used when sending the request.\\nDefault value\\: Undefined. If the configuration uses SSL (Standard Subsystems Library),\\nthe proxy values will be taken from SSL.",

    # BuildNewURLOnRedirect comment
    "Method.СформироватьНовыйURLПриПеренаправлении.Comment.Редирект\\ без\\ схемы.Description":
        "Redirect without scheme",

    # Region comments (long region paths)
    "Region.ПрограммныйИнтерфейс.СлужебныйПрограммныйИнтерфейс.СлужебныеПроцедурыИФункции.РаботаСHTTPЗапросами.ОбработчикиСобытий.URL.РаботаССоединением.Заголовки.Cookies.ПараметрыРаботыСJSON.АутентификацияAWS4.КодированиеДекодированиеДанных.СлужебныеСтруктурыZip.Comment.Описание\\ структур\\nhttps\\://pkware\\.cachefly\\.net/webdocs/casestudies/APPNOTE\\.TXT.Description":
        "Structure description see here https\\://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT",
    "Region.ПрограммныйИнтерфейс.СлужебныйПрограммныйИнтерфейс.СлужебныеПроцедурыИФункции.РаботаСHTTPЗапросами.ОбработчикиСобытий.URL.РаботаССоединением.Заголовки.Cookies.ПараметрыРаботыСJSON.АутентификацияAWS4.КодированиеДекодированиеДанных.СлужебныеСтруктурыZip.СлужебныеСтруктурыGZip.Comment.Описание\\ структур\\nhttps\\://www\\.ietf\\.org/rfc/rfc1952\\.txt.Description":
        "Structure description see here https\\://www.ietf.org/rfc/rfc1952.txt",
}
