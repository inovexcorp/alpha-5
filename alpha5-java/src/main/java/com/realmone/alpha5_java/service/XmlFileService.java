package com.realmone.alpha5_java.service;

import com.realmone.alpha5_java.entity.XmlFile;
import com.realmone.alpha5_java.repository.XmlFileRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class XmlFileService {
    @Autowired
    private XmlFileRepository xmlFileRepository;

    public XmlFile createXmlFile(XmlFile xmlFile) {
        return xmlFileRepository.save(xmlFile);
    }

    public void loadXmlFiles(List<XmlFile> xmlFiles) {
        xmlFileRepository.saveAll(xmlFiles);
    }

    public XmlFile getXmlFileByIdentifier(String id) {
        return xmlFileRepository.findByIdentifier(id);
    }

    public List<XmlFile> getAllXmlFiles() {
        return xmlFileRepository.findAll();
    }

    public void deleteXmlFileByIdentifier(String id) {
        xmlFileRepository.deleteByIdentifier(id);
    }

    public void deleteAllXmlFiles() {
        xmlFileRepository.deleteAll();
    }

}
