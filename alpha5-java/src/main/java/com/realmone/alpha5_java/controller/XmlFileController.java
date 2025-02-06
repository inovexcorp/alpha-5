package com.realmone.alpha5_java.controller;

import com.realmone.alpha5_java.entity.XmlFile;
import com.realmone.alpha5_java.service.XmlFileService;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping(value = "/api/xml")
public class XmlFileController {

    @Autowired
    private XmlFileService xmlFileService;

    @GetMapping("/{id}")
    public XmlFile getXmlFile(@PathVariable String id) {
        return xmlFileService.getXmlFileByIdentifier(id);
    }

    @GetMapping
    public List<XmlFile> getAllXmlFiles() {
        return xmlFileService.getAllXmlFiles();
    }

    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    public XmlFile postXmlFile(@RequestBody XmlFile xmlFile) {
        return xmlFileService.createXmlFile(xmlFile);
    }

    @PostMapping(path = "/load",consumes = MediaType.APPLICATION_JSON_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    public void loadXmlFiles(@RequestBody List<XmlFile> xmlFiles) {
        xmlFileService.loadXmlFiles(xmlFiles);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.OK)
    @Transactional
    public void deleteXmlFiles(@PathVariable String id) {
        xmlFileService.deleteXmlFileByIdentifier(id);
    }

    @DeleteMapping("/danger")
    @ResponseStatus(HttpStatus.I_AM_A_TEAPOT)
    @Transactional
    public void deleteAllXmlFiles() {
        xmlFileService.deleteAllXmlFiles();
    }
    // DO NOT IMPLEMENT THIS ENDPOINT IN THE FRONTEND, BRO! IT'S ONLY FOR TESTING/DEV!

}
